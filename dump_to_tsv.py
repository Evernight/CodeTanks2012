import pickle

data = pickle.load(open('targets.dump', 'rb'))

with open('targets.dump', 'w') as f:
    f.write('\t'.join(['direction_angle', 'distance', 'velocity_angle', 'velocity', 'angular_speed']))
    f.write('\n'.join(map(lambda x: '%s\t' * 5 + '%s' % x, data)))