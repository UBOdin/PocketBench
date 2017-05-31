package com.example.benchmark_withjson;

import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteException;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;

public class Queries {

    JSONObject workloadJsonObject;
    Context context;
    Utils utils;

    public Queries(Context inContext){
        utils = new Utils();
        workloadJsonObject = Utils.workloadJsonObject;
        context = inContext;
    }

    public int startQueries(){
        utils.putMarker("{\"EVENT\":\"Workload A BDB\"}", "trace_marker");

        utils.putMarker("START: App started\n", "trace_marker");


/*
        utils.putMarker("{\"EVENT\":\"SQL_START\"}", "trace_marker");

        int tester = sqlQueries();
        if(tester != 0){
            return 1;
        }

        utils.putMarker("{\"EVENT\":\"SQL_END\"}", "trace_marker");
*/
///*
        utils.putMarker("{\"EVENT\":\"BDB_START\"}", "trace_marker");

        int tester = bdbQueries();
        if (tester != 0){
            return 1;
        }

        utils.putMarker("{\"EVENT\":\"BDB_END\"}", "trace_marker");

//*/
        utils.putMarker("END: app finished\n", "trace_marker");

        return 0;
    }

    private int sqlQueries(){

        SQLiteDatabase db = context.openOrCreateDatabase("SQLBenchmark",0,null);
        int sqlException = 0;

        try {
            JSONArray benchmarkArray = workloadJsonObject.getJSONArray("benchmark");
            for(int i = 0; i < benchmarkArray.length(); i ++){
                JSONObject operationJson = benchmarkArray.getJSONObject(i);
                Object operationObject = operationJson.get("op");
                String operation = operationObject.toString();

                switch (operation) {
                    case "query": {
                        sqlException = 0;
                        Object queryObject = operationJson.get("sql");
                        String query = queryObject.toString();

                        try {

                            if(query.contains("SELECT")){
                                Cursor cursor = db.rawQuery(query,null);
                                if(cursor.moveToFirst()) {
                                    int numColumns = cursor.getColumnCount();
                                    do {
                                        int j=0;
                                        while (j< numColumns) {
                                            j++;
                                        }
                                    } while(cursor.moveToNext());
                                }
                                cursor.close();
                            }
                            else {
                                db.execSQL(query);
                            }

                        }
                        catch (SQLiteException e){
                            sqlException = 1;
                            continue;
                        }
                        break;
                    }
                    case "break": {

                        if(sqlException == 0) {
                            Object breakObject = operationJson.get("delta");
                            int breakTime = Integer.parseInt(breakObject.toString());
                            int tester = utils.sleepThread(breakTime);
                            if(tester != 0){
                                return 1;
                            }

                        }
                        sqlException = 0;
                        break;
                    }
                    default:
                        db.close();
                        return 1;
                }

            }

        } catch (JSONException e) {
            e.printStackTrace();
            db.close();
            return 1;
        }
        db.close();
        return 0;
    }

    private int bdbQueries(){

        Connection con = utils.jdbcConnection("BDBBenchmark");
        Statement stmt;
        int sqlException = 0;

        try {
            JSONArray benchmarkArray = workloadJsonObject.getJSONArray("benchmark");
            for(int i = 0; i < benchmarkArray.length(); i ++){
                JSONObject operationJson = benchmarkArray.getJSONObject(i);
                Object operationObject = operationJson.get("op");
                String operation = operationObject.toString();
                switch (operation) {
                    case "query": {
                        sqlException = 0;
                        Object queryObject = operationJson.get("sql");
                        String query = queryObject.toString();

                        try {

                            stmt = con.createStatement();
                            if(query.contains("UPDATE")){
                                int tester = stmt.executeUpdate(query);
                                if(tester == 0 || tester < 0){
                                    stmt.close();
                                }
                            }
                            else {
                                Boolean test = stmt.execute(query);
                                if (!test){
                                    stmt.close();
                            }
                            stmt.close();


                            }
                        }
                        catch (SQLiteException e){
                            sqlException = 1;
                            
                            continue;
                        } catch (SQLException e) {
                            sqlException = 1;

                            e.printStackTrace();
                            continue;
                        }
                        break;
                    }
                    case "break": {

                        if(sqlException == 0) {
                            Object breakObject = operationJson.get("delta");
                            int breakTime = Integer.parseInt(breakObject.toString());
                            int tester = utils.sleepThread(breakTime);
                            if(tester != 0){
                                return 1;
                            }

                        }
                        sqlException = 0;
                        break;
                    }
                    default:
                        con.close();
                        return 1;
                }

            }
        } catch (JSONException e) {
            e.printStackTrace();

            try {
                con.close();
            } catch (SQLException e1) {
                e1.printStackTrace();
            }

            return 1;
        } catch (SQLException e) {
            e.printStackTrace();
            return 1;
        }

        try {
            con.close();
        } catch (SQLException e) {
            e.printStackTrace();
            return 1;
        }

        return 0;
    }

}
