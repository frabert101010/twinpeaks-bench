from run_full_benchmark import BenchmarkRunner

if __name__ == "__main__":
    print("\n🚀 Continuing TwinPeaks Bench V1 Evaluation from Question 22")
    print("=" * 70)
    print("NOTE: This will ONLY run WITH SEARCH mode starting from twin_peaks_022")
    print("=" * 70)

    runner = BenchmarkRunner()
    runner.run_benchmark(
        eval_file='eval_set_v1.json',
        num_trials=3,
        start_from_question='twin_peaks_022',
        search_mode_only=True
    )
