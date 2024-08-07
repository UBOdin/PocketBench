package com.example.benchmark_withjson;

import android.app.ActivityManager;
import android.content.Context;
import android.os.Environment;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;

public class Utils {

    static JSONObject workloadJsonObject;

    // Additional global config parameters:
    static String database;
    static String workload;
    static String governor;
    static String speed;
    static String delay;

    public static String jsonToString(Context context, int workload){

        String line;
        String finalString = "";

        try {

            InputStream is = context.getResources().openRawResource(workload);
            BufferedReader br = new BufferedReader(new InputStreamReader(is));

            finalString = br.readLine();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return finalString;
    }

    public static JSONObject jsonStringToObject(String jsonString){
        JSONObject jsonObject = null;
        try {
            jsonObject = new JSONObject(jsonString);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        workloadJsonObject = jsonObject;
        return jsonObject;
    }

    public static int sleepThread(int interval) {

        // Adjust delay time if necessary -- default is lognormal distribution, per parameter:
        if (Utils.delay.equals("0ms")) {
            interval = 0;
        }
        if (Utils.delay.equals("1ms")) {
            interval = 1;
        }

        try {
            Thread.sleep(interval);
        } catch (Exception e) {
            e.printStackTrace();
            return 1;
        }
        return 0;
    }


    public static Connection jdbcConnection(String dbName) {
        if(dbName == null){
            return null;
        }
        String url =
                "jdbc:sqlite://data/data/com.example.benchmark_withjson/databases/" + dbName;
        Connection con;
        try {
            Class.forName("SQLite.JDBCDriver");


        } catch (java.lang.ClassNotFoundException e) {
            System.err.print("ClassNotFoundException: ");
            System.err.println(e.getMessage());
            return null;
        }

        try {
            con = DriverManager.getConnection(url);

        } catch (SQLException e) {
            e.printStackTrace();
            return null;
        }

        return con;
    }

    public static int findMissingQueries(Context context){

        // Signal calling script that benchmark run has finished:
        try {
            FileWriter file_writer = new FileWriter("/data/results.pipe");
            BufferedWriter buffered_writer = new BufferedWriter(file_writer);
            buffered_writer.write("This is a test.  This is only a test.  Testing 357 testing.\n");
            buffered_writer.close();
        } catch(IOException exception) {
            System.out.println("FOOBAR Error on writing unblock signal");
            exception.printStackTrace();
        }

        return 0;
    }

    public static int putMarker(String mark) {
        PrintWriter outStream = null;
        try{
            FileOutputStream fos = new FileOutputStream("/sys/kernel/debug/tracing/trace_marker");
            outStream = new PrintWriter(new OutputStreamWriter(fos));
            outStream.println(mark);
            outStream.flush();
        }
        catch(Exception e) {
            Log.d("benchmark_withjson",e.toString());
            return 1;
        }
        finally {
            if (outStream != null) {
                outStream.close();
            }
        }
        return 0;
    }

/*
    public static boolean doesDBExist(Context context, String dbPath){
        File dbFile = context.getDatabasePath(dbPath);
        return dbFile.exists();
    }
*/

}
