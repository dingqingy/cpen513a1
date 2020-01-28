from routing import Router

all_benchmarks = [
	'example', 
	'impossible', 
	'impossible2',
	'kuma', 
	'misty',
	'oswald',
	'rusty',
	'stanley',
	'stdcell',
	'sydney',
	'temp',
	'wavy'
]

if __name__ == '__main__':
	for benchmark in all_benchmarks:
		router = Router('benchmarks/'+benchmark+'.infile')
		router.routeAll()
		print('benchmark {}: {} / {} segments routed!'.format(benchmark, router.best_total_segments, router.total_possible_segments))