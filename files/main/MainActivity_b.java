package com.example.benchmark_withjson;

import android.app.ActivityManager;
import android.content.Context;
import android.provider.Settings;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import android.app.ActivityManager.*;




public class MainActivity extends AppCompatActivity implements Runnable {
    static int a[];

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        //setContentView(R.layout.activity_main);

        this.run();
    }

    @Override
    public void run() {

        android.os.Process.setThreadPriority(android.os.Process.THREAD_PRIORITY_BACKGROUND);

        //final int workload_a_timing_a = R.raw.workload_a_timing_a;
        final int workload_b_timing_a = R.raw.workload_b_timing_a;
        //final int workload_c_timing_a = R.raw.workload_c_timing_a;
        //final int workload_d_timing_a = R.raw.workload_d_timing_a;
        //final int workload_e_timing_a = R.raw.workload_e_timing_a;
        //final int workload_f_timing_a = R.raw.workload_f_timing_a;
        //final int workload_ia_timing_a = R.raw.workload_ia_timing_a;
        //final int workload_ib_timing_a = R.raw.workload_ib_timing_a;
        //final int workload_ic_timing_a = R.raw.workload_ic_timing_a;
        //final int workload_id_timing_a = R.raw.workload_id_timing_a;

        Utils utils = new Utils();

        long start = System.currentTimeMillis();
        int tester;

        if(!utils.doesDBExist(this,"BDBBenchmark")){
            //Create the databases from the JSON
            CreateDB createDB = new CreateDB(this);
            tester = createDB.create(workload_b_timing_a);
            if(tester != 0){
                this.finishAffinity();
            }
            this.finishAffinity();
        }
        else {

            String singleJsonString = utils.jsonToString(this, workload_b_timing_a);
            utils.jsonStringToObject(singleJsonString);


            //Run the queries specified in the JSON on the newly created databases
            Queries queries = new Queries(this);
            tester = queries.startQueries();
            if (tester != 0){
                this.finishAffinity();
            }

            //Find what queries were not executed successfully in the SQL or BDB traces
            utils.findMissingQueries(this);
            //Calculate total time of the traces
            long end = System.currentTimeMillis();

            long delta = end - start;
            double elapsedSeconds = delta / 1000.0;

            File file = new File(this.getFilesDir().getPath() + "/time");
            FileOutputStream fos;
            try {
                fos = this.openFileOutput(file.getName(), Context.MODE_APPEND);
                fos.write((elapsedSeconds + "\n").getBytes());
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
