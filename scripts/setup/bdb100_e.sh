# setup workload e, bdb100
rm apps/Benchmark_withJson/app/src/main/java/com/example/benchmark_withjson/Queries.java
rm apps/Benchmark_withJson/app/src/main/java/com/example/benchmark_withjson/MainActivity.java
cp files/main/MainActivity_e.java apps/Benchmark_withJson/app/src/main/java/com/example/benchmark_withjson/MainActivity.java
cp files/bdb/100MB/Queries_e.java apps/Benchmark_withJson/app/src/main/java/com/example/benchmark_withjson/Queries.java
