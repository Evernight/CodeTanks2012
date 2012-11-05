import pickle

data = pickle.load(open('targets.dump', 'rb'))

with open('targets.tab', 'w') as f:
    print()
    f.write('\t'.join(['direction_angle', 'distance', 'velocity_angle', 'velocity', 'angular_speed', 'health', 'time']))
    f.write('\n')
    f.write('\t'.join(['c', 'c', 'c', 'c', 'c', 'c', 'c']))
    f.write('\n')
    f.write('\n')
    f.write('\n'.join(map(lambda x: '%f\t%f\t%f\t%f\t%f\t%f\t%f' % x, data)))