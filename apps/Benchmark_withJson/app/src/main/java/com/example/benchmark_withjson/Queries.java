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

import android.util.Log;

import java.util.concurrent.locks.*;

import java.lang.Math.*;

public class Queries {

    static Connection con = null;
    static SQLiteDatabase db = null;

    static JSONArray benchmarkArray;
    static int operation_total;

    int _thread_number;
    int _first_operation;
    int _last_operation;

    public Queries(int thread_number){

        this._thread_number = thread_number;
        this._first_operation = Math.round((float)thread_number * (float)Queries.operation_total / (float)Worker.thread_count);
        this._last_operation = Math.round((float)(thread_number + 1) * (float)Queries.operation_total / (float)Worker.thread_count);

    }

    public static void init_db_handle(Context context) {

        if ((Utils.database.equals("SQL")) || (Utils.database.equals("WAL"))) {
		db = context.openOrCreateDatabase("SQLBenchmark",0,null);
	} else if ((Utils.database.equals("BDB")) || (Utils.database.equals("BDB100"))) {
		con = Utils.jdbcConnection("BDBBenchmark");
	}

	try {
		Queries.benchmarkArray = Utils.workloadJsonObject.getJSONArray("benchmark");
		Queries.operation_total = Queries.benchmarkArray.length();
        } catch (JSONException e) {
		e.printStackTrace();
		return;
        }
 
	return;

    }

    public static void close_db_handle() {

	if (db != null) {
			db.close();
	}
	if (con != null) {
		try {
			con.close();
		} catch (SQLException e) {
			e.printStackTrace();
			return;
		}
	}
    }

    public int startQueries(int thread_number){

	int tester;
	String PDE = "PocketData";

	Log.d(PDE, "Start startQueries()");
	Utils.putMarker("{\"EVENT\":\"Parameters\", \"Database\":\"" + Utils.database + "\", \"Workload\":\"" + Utils.workload + "\", \"Governor\":\"" + Utils.governor + "\", \"Speed\":\"" + Utils.speed + "\", \"Delay\":\"" + Utils.delay + "\"}");
	Utils.putMarker("START: App started\n");
	Utils.putMarker("{\"EVENT\":\"" + Utils.database + "_START\", \"thread\":" + thread_number + "}");

	if ((Utils.database.equals("SQL")) || (Utils.database.equals("WAL"))) {
		Log.d(PDE, "Testing SQL");
		tester = sqlQueries();
	} else if ((Utils.database.equals("BDB")) || (Utils.database.equals("BDB100"))) {
		Log.d(PDE, "Testing BDB");
		tester = bdbQueries();
	} else {
		Log.d(PDE, "Error -- Unknown Database Requested");
		return 1;
	}
	if (tester != 0) {
		Log.d(PDE, "Error -- Bad Benchmark Result");
		return 1;
	}

	Log.d(PDE, "End startQueries()");
	Utils.putMarker("{\"EVENT\":\"" + Utils.database + "_END\", \"thread\":" + thread_number + "}");
	Utils.putMarker("END: app finished\n");

	return 0;

    }

    private int sqlQueries(){

        int sqlException = 0;

        try {

            for (int i = this._first_operation; i < this._last_operation; i++) {
                JSONObject operationJson = Queries.benchmarkArray.getJSONObject(i);

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
                            int tester = Utils.sleepThread(breakTime);
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
        return 0;
    }

    private int bdbQueries(){

        Statement stmt;
        int sqlException = 0;

        try {

            for (int i = this._first_operation; i < this._last_operation; i++) {
                JSONObject operationJson = Queries.benchmarkArray.getJSONObject(i);

                Object operationObject = operationJson.get("op");
                String operation = operationObject.toString();
                switch (operation) {
                    case "query": {
                        sqlException = 0;
                        Object queryObject = operationJson.get("sql");
                        String query = queryObject.toString();

                        try {

Utils.putMarker("PDE Start op");

                            stmt = con.createStatement();

                            if(query.contains("UPDATE")){
                                int tester = stmt.executeUpdate(query);
//                                if(tester == 0 || tester < 0){
                                    stmt.close();
//                                }
                            }
                            else {
                                Boolean test = stmt.execute(query);
//                                if (!test){
//                                    stmt.close();
//	                        }
                                stmt.close();


                            }

Utils.putMarker("PDE Stop op");

                        }
                        catch (SQLiteException e){
                            sqlException = 1;

Utils.putMarker("PDE Error 1");

                            continue;
                        } catch (SQLException e) {
                            sqlException = 1;

Utils.putMarker("PDE Error 2");

                            e.printStackTrace();
                            continue;
                        }
                        break;
                    }
                    case "break": {

                        if(sqlException == 0) {
                            Object breakObject = operationJson.get("delta");
                            int breakTime = Integer.parseInt(breakObject.toString());
                            int tester = Utils.sleepThread(breakTime);
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
        return 0;
    }

}
