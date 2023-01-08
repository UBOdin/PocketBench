package com.example.test;

import android.content.Context;
import android.content.Intent;
import android.util.Log;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;

import androidx.test.core.app.ApplicationProvider;
import androidx.test.filters.SdkSuppress;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.runner.AndroidJUnit4;
import androidx.test.uiautomator.UiDevice;
import androidx.test.uiautomator.By;
import androidx.test.uiautomator.UiSelector;
import androidx.test.uiautomator.Until;


@RunWith(AndroidJUnit4.class)
@SdkSuppress(minSdkVersion = 18)
public class BankTest {

    private static final String TEST_PACKAGE = "com.facebook.katana";
    private static final int LAUNCH_TIMEOUT = 5000;
    private static final String STRING_TO_BE_TYPED = "UiAutomator";
    private UiDevice device;
    String logflag = "TESTFLAG";

    @Before
    public void startMainActivityFromHomeScreen() {
        // Initialize UiDevice instance
        device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());

        // Start from the home screen
        device.pressHome();

        // Wait for launcher
        final String launcherPackage = device.getLauncherPackageName();
        //assertThat(launcherPackage, notNullValue());
        device.wait(Until.hasObject(By.pkg(launcherPackage).depth(0)),
                LAUNCH_TIMEOUT);

        // Launch the app
        Context context = ApplicationProvider.getApplicationContext();

        final Intent intent = context.getPackageManager()
                .getLaunchIntentForPackage(TEST_PACKAGE);

        Log.d(logflag, "pointer:  " + intent);

        // Clear out any previous instances
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK);
        context.startActivity(intent);

        Log.d(logflag, "Before");

        // Wait for the app to appear
        device.wait(Until.hasObject(By.pkg(TEST_PACKAGE).depth(0)),
                LAUNCH_TIMEOUT);

        Log.d(logflag, "After");

    }

    @Test
    public void PunchKeys() {

        Log.d(logflag, "Start FB Test");

        try {
            // Navigate to friends list:
            Thread.sleep(1000);
            device.click(270, 280);
            Thread.sleep(1000);
            device.click(490, 370);
            Thread.sleep(1000);
            device.swipe(500, 1200, 500, 800, 10);
            // Scroll through friends list:
            Thread.sleep(500);
            device.swipe(500, 1200, 500, 800, 10);
            Thread.sleep(500);
            device.swipe(500, 1200, 500, 800, 10);
            Thread.sleep(500);
            device.swipe(500, 1200, 500, 800, 10);
            Thread.sleep(500);
            device.swipe(500, 1200, 500, 800, 10);
            Thread.sleep(500);
            device.swipe(500, 1200, 500, 800, 10);
            // Go back to app home:
            Thread.sleep(1000);
            device.pressBack();
            Thread.sleep(500);
            device.pressBack();
            Thread.sleep(500);
            // Scroll through feed:
            for (int i = 0; i < 20; i++) {
                device.swipe(500, 1300, 500, 600, 10);
                Thread.sleep(500);
            }

        } catch (Exception e) {
            Log.d(logflag, "Exception Catch:  " + e.toString());
        }

    }

}