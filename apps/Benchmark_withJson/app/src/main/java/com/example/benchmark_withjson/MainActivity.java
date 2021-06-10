package com.example.benchmark_withjson;

import android.app.ActivityManager;
import android.content.Context;
import android.provider.Settings;
//import android.support.v7.app.AppCompatActivity;
import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import android.app.ActivityManager.*;

import android.util.Log;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.util.concurrent.locks.*;
import java.lang.InterruptedException;


public class MainActivity extends AppCompatActivity /*implements Runnable*/ {
    static int a[];
    static String PDE = "PocketData";

    static {
        System.loadLibrary("perflib");
    }

    public static native int startcount(int dummy);
    public static native int stopcount(int dummy);

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        final int[] workload_array = {
                R.raw.workload_a_single_line, R.raw.workload_b_single_line,
                R.raw.workload_c_single_line, R.raw.workload_d_single_line,
                R.raw.workload_e_single_line, R.raw.workload_f_single_line,
                R.raw.workload_ia_single_line, R.raw.workload_ib_single_line,
                R.raw.workload_ic_single_line,
        };

        // Map workload handle to ASCII input:
        String[] workloads = {"A", "B", "C", "D", "E", "F", "IA", "IB", "IC"};
        HashMap<String, Integer> load_map = new HashMap<String, Integer>();
        for (int i = 0; i < workloads.length; i++) {
            load_map.put(workloads[i], workload_array[i]);
        }
        load_map.put("N", workload_array[2]);  // Dummy map for null workload

        // Pull in setup parameters from on-phone shell script:
        FileReader file_reader;
        BufferedReader buffered_reader;
        String input_line = null;
        try {
            file_reader = new FileReader("/data/config.txt");
            buffered_reader = new BufferedReader(file_reader);
            Utils.database = buffered_reader.readLine().toUpperCase();
            Utils.workload = buffered_reader.readLine().toUpperCase();
            Utils.governor = buffered_reader.readLine();
            Utils.speed = buffered_reader.readLine();
            Utils.delay = buffered_reader.readLine();
            Worker.thread_count = Integer.parseInt(buffered_reader.readLine());
            file_reader.close();
        } catch (IOException exception) {
            exception.printStackTrace();
            return;
        }

        Log.d(PDE, "Parameter Database:  " + Utils.database);
        Log.d(PDE, "Parameter Workload:  " + Utils.workload);
//	Log.d(PDE, "Parameter WL handle:  " + load_map.get(Utils.workload));  // sanity check on hashmap
        Log.d(PDE, "Parameter Governor:  " + Utils.governor);
        Log.d(PDE, "Parameter Speed:  " + Utils.speed);
        Log.d(PDE, "Parameter Delay:  " + Utils.delay);


        long start = System.currentTimeMillis();
        int tester;

//        if(!Utils.doesDBExist(this,"BDBBenchmark")){
        if (!Queries.db_exists()) {
            Log.d(PDE, "Creating DB");
            //Create the databases from the JSON
            CreateDB createDB = new CreateDB(this);
            tester = createDB.create(load_map.get(Utils.workload));
            if(tester != 0){
                this.finishAffinity();
            }
            this.finishAffinity();
            return;
        }

        Log.d(PDE, "DB exists -- Running DB Benchmark");

        String singleJsonString = Utils.jsonToString(this, load_map.get(Utils.workload));
        Utils.jsonStringToObject(singleJsonString);

        if (Utils.workload.equals("N") == true) {

            // Log null workload to tracefile and exit:
            Utils.putMarker("{\"EVENT\":\"Parameters\", \"Database\":\"" + Utils.database + "\", \"Workload\":\"" + Utils.workload + "\", \"Governor\":\"" + Utils.governor + "\", \"Speed\":\"" + Utils.speed + "\", \"Delay\":\"" + Utils.delay + "\"}");

        } else {

            // Signal perf to start collecting cycles:
            Log.d(PDE, "startcount() retval:  " + startcount(1));
            // Set up DB handle:
            Queries.init_db_handle(this);

//		Queries queries = new Queries();
//		queries.startQueries(0);  // Single thread (0)


            // Init synch primitives:
            Worker.lock = new ReentrantLock();
            Worker.condition = Worker.lock.newCondition();

            Worker.threads_left = Worker.thread_count;

            // Fork off worker threads:
            for (int i = 0; i < Worker.thread_count; i++) {
                Worker w = new Worker(i);
                Thread t = new Thread(w);
                t.start();
            }

            // Block until workers finish:
            Worker.lock.lock();
            while (Worker.threads_left > 0) {
                try {
                    Worker.condition.await();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                    this.finishAffinity();
                    return;
                }
            }
            Worker.lock.unlock();


            // Close DB handle:
            Queries.close_db_handle();
            // Stop collecting cycles:
            Log.d(PDE, "stopcount() retval:  " + stopcount(0));

        }

        // Signal scripting app we are done (subroutine repurposed):
        Utils.findMissingQueries(this);

        this.finishAffinity();
        return;

    }

}


class Worker implements Runnable {

    static Lock lock;
    static Condition condition;
    static int thread_count;
    static int threads_left;  // number of threads still running

    int _thread_number;  // Our in-house TID

    public Worker(int thread_number) {

        this._thread_number = thread_number;
        return;

    }

    public void run() {

        Queries queries = new Queries(this._thread_number);
        queries.startQueries(this._thread_number);

        // Signal main thread we are done:
        Worker.lock.lock();
        Worker.threads_left--;
        if (Worker.threads_left == 0) {
            Worker.condition.signal();
        }
        Worker.lock.unlock();

        return;

    }

}
