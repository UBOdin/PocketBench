# setup workload ib, sql
rm apps/Benchmark_withJson/app/src/main/java/com/example/benchmark_withjson/Queries.java
rm apps/Benchmark_withJson/app/src/main/java/com/example/benchmark_withjson/MainActivity.java
cp files/main/MainActivity_ib.java apps/Benchmark_withJson/app/src/main/java/com/example/benchmark_withjson/MainActivity.java
cp files/wal/Queries_ib.java apps/Benchmark_withJson/app/src/main/java/com/example/benchmark_withjson/Queries.java
