# Copyright (C) 2020 Intel Corporation
# Licensed subject to the terms of the separately executed
# evaluation license agreement between Intel Corporation and you.

import numpy as np

from .assigner import Assigner


class RandomGroupedAssigner(Assigner):
    """
    The task assigner maintains a list of tasks, and decides the policy for which collaborator should run those tasks
    There may be many types of policies implemented, but a natural place to start is with a:

    RandomGroupedAssigner  - Given a set of task groups, and a percentage, assign that task group to that percentage
                             of collaborators in the federation. After assigning the tasks to collaborator, those
                             tasks should be carried out each round (no reassignment between rounds)
    GroupedAssigner -        Given task groups and a list of collaborators that belong to that task group,
                             carry out tasks for each round of experiment
    """

    def __init__(self, task_groups, tasks, authorized_cols, rounds_to_train, **kwargs):

        self.task_groups = task_groups
        self.tasks = tasks
        self.rounds = rounds_to_train
        self.authorized_cols = authorized_cols

        self.task_group_collaborators = {}
        self.collaborators_for_task = {}
        self.collaborator_tasks = {}

        self.define_task_assignments()

    def define_task_assignments(self):
        """
        All of the logic to set up the map of tasks to collaborators is done here
        """

        assert (np.abs(1.0 - np.sum([group['percentage'] for group in self.task_groups])) < 0.01), (
            'Task group percentages must sum to 100%')

        # Start by finding all of the tasks in all specified groups
        self.all_tasks_in_groups = list(set([task for group in self.task_groups for task in group['tasks']]))

        # Initialize the map of collaborators for a given task on a given round
        for task in self.all_tasks_in_groups:
            self.collaborators_for_task[task] = {i: [] for i in range(self.rounds)}

        for col in self.authorized_cols:
            self.collaborator_tasks[col] = {i: [] for i in range(self.rounds)}

        col_list_size = len(self.authorized_cols)
        for round_num in range(self.rounds):
            randomized_col_idx = np.random.choice(len(self.authorized_cols), len(self.authorized_cols), replace=False)
            col_idx = 0
            for group in self.task_groups:
                num_col_in_group = int(group['percentage'] * col_list_size)
                rand_col_group_list = [self.authorized_cols[i] for i in
                                       randomized_col_idx[col_idx:col_idx + num_col_in_group]]
                self.task_group_collaborators[group['name']] = rand_col_group_list
                for col in rand_col_group_list:
                    self.collaborator_tasks[col][round_num] = group['tasks']
                # Now populate reverse lookup of tasks->group
                for task in group['tasks']:
                    # This should append the list of collaborators performing that task
                    self.collaborators_for_task[task][round_num] += rand_col_group_list
                col_idx += num_col_in_group
            assert (col_idx == col_list_size), 'Task groups were not divided properly'

    def get_tasks_for_collaborator(self, collaborator_name, round_number):
        return self.collaborator_tasks[collaborator_name][round_number]

    def get_collaborators_for_task(self, task_name, round_number):
        return self.collaborators_for_task[task_name][round_number]

    def get_aggregation_type_for_task(self, task_name):
        if 'aggregation_type' not in self.tasks[task_name]:
            return None
        return self.tasks[task_name]['aggregation_type']

    def get_all_tasks_for_round(self, round_number):
        """
        Currently all tasks are performed on each round, but there may be a reason to change this
        """
        return self.all_tasks_in_groups
