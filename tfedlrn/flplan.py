import yaml

def load_flplan(path):
    plan = None
    with open(path, 'r') as f:
        plan = yaml.safe_load(f.read())
    return plan
