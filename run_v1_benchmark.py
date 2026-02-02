from run_full_benchmark import BenchmarkRunner

if __name__ == "__main__":
    print("\n🚀 Running TwinPeaks Bench V1 Evaluation")
    print("=" * 70)

    runner = BenchmarkRunner()
    runner.run_benchmark(eval_file='eval_set_v1.json', num_trials=3)
