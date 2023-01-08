package com.example.test;

import android.os.Bundle;
import android.util.Log;

import androidx.appcompat.app.AppCompatActivity;


public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    @Override
    protected void onStart () {
        super.onStart();

        Log.d("TESTFOO", "On Start Test");

    }

    @Override
    protected void onResume() {
        super.onResume();

        Log.d("TESTFOO", "On Resume Test");

    }

    @Override
    protected void onPause() {
        super.onPause();

        Log.d("TESTFOO", "On Pause Test");

    }

    @Override
    protected void onStop() {
        super.onStop();

        Log.d("TESTFOO", "On Stop Test");

    }

}
