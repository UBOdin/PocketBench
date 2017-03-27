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




public class MainActivity extends AppCompatActivity {
    static int a[];

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        //final int workload_a_timing_a = R.raw.workload_a_timing_a;
        //final int workload_b_timing_a = R.raw.workload_b_timing_a;
        //final int workload_c_timing_a = R.raw.workload_c_timing_a;
        //final int workload_d_timing_a = R.raw.workload_d_timing_a;
        //final int workload_e_timing_a = R.raw.workload_e_timing_a;
        //final int workload_f_timing_a = R.raw.workload_f_timing_a;
        //final int workload_ia_timing_a = R.raw.workload_ia_timing_a;
        final int workload_ib_timing_a = R.raw.workload_ib_timing_a;
        //final int workload_ic_timing_a = R.raw.workload_ic_timing_a;
        //final int workload_id_timing_a = R.raw.workload_id_timing_a;

        Utils utils = new Utils();

        //long memNow = utils.memoryAvailable(this);

        //utils.restrictHeapTo12_5();

        //long memafter = utils.memoryAvailable(this);

        long start = System.currentTimeMillis();
        int tester;

        /*
        File file2 = new File(this.getFilesDir().getPath() + "/start_end");
        //File file = new File("/data/BDBtime");
        FileOutputStream fos2;
        try {
            fos2 = this.openFileOutput(file2.getName(), Context.MODE_APPEND);
            fos2.write(("Start: " + start + "\n").getBytes());;
        } catch (IOException e) {
            e.printStackTrace();
        }

        utils.putMarker("{\"EVENT\":\"testing\"}", "trace_marker");

        this.finishAffinity();
        */


        if(!utils.doesDBExist(this,"BDBBenchmark")){
            //Create the databases from the JSON
            CreateDB createDB = new CreateDB(this);
            tester = createDB.create(workload_ib_timing_a);
            if(tester != 0){
                this.finishAffinity();
            }
            this.finishAffinity();
        }
        else {

            //utils.restrictHeapTo25();

            String singleJsonString = utils.jsonToString(this, workload_ib_timing_a);
            utils.jsonStringToObject(singleJsonString);


            //Run the queries specified in the JSON on the newly created databases
            Queries queries = new Queries(this);
            tester = queries.startQueries();
            if (tester != 0){
                this.finishAffinity();
            }

            //Find what queries were not executed successfully in the SQL or BDB traces
            utils.findMissingQueries(this);
            /*
            int tester2 = utils.findMissingQueries(this);
            if(tester2 != 0){
                this.finishAffinity();
            }
            */
            //Calculate total time of the traces
            long end = System.currentTimeMillis();

            long delta = end - start;
            double elapsedSeconds = delta / 1000.0;

            /*
            ActivityManager.MemoryInfo mi = new ActivityManager.MemoryInfo();
            ActivityManager activityManager = (ActivityManager) this.getSystemService(Context.ACTIVITY_SERVICE);
            activityManager.getMemoryInfo(mi);
            long total = mi.totalMem;
            */


            File file = new File(this.getFilesDir().getPath() + "/time");
            //File file = new File("/data/BDBtime");
            FileOutputStream fos;
            try {
                fos = this.openFileOutput(file.getName(), Context.MODE_APPEND);
                fos.write((elapsedSeconds + "\n").getBytes());
                //fos.write(("Mem total: " + total + "\n").getBytes());
                //fos.write(("Mem at start: " + memNow + "\n").getBytes());
                //fos.write(("Mem after heap allocation: " + memafter + "\n").getBytes());
                //fos.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        //this.finishAffinity();
        }
    }
}
