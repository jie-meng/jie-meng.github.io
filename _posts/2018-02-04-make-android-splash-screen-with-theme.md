---
title: Make Android splash screen with theme
layout: post
date: 2018-02-04 10:57:03 +0800
categories: android
---

Make Android splash screen with theme is more simpler than create a Splash Activity.

The first thing you need to do is define a Launcher style in style.xml.

@drawable/splash_screen is the image you use in splash screen.

{% highlight xml %}

<style name="AppThemeBase.Launcher" parent="Theme.AppCompat.Light.NoActionBar">
    <item name="android:textColor">@android:color/black</item>
    <item name="android:windowNoTitle">true</item>
    <item name="windowActionBar">false</item>
    <item name="android:windowFullscreen">true</item>
    <item name="android:windowContentOverlay">@null</item>
    <item name="android:windowBackground">@drawable/splash_screen</item>
</style>

{% endhighlight %}

Then use the theme in MainActivity (Your launcher Activity).

{% highlight java %}

<activity android:name=".MainActivity"
    android:alwaysRetainTaskState="true"
    android:screenOrientation="portrait"
    android:windowSoftInputMode="adjustPan"
    android:theme="@style/AppThemeBase.Launcher">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>

{% endhighlight %}

Then Implement MainActivity. Reset theme after show Splash screen for 1500 ms.

{% highlight java %}

public class MainActivity extends AppCompatActivity {

    public static final String ARG_SHOW_LOGIN = "arg_show_login";

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        //prevent multiple instances of an activity when it is launched with different intents
        if (!isTaskRoot()
                && getIntent().hasCategory(Intent.CATEGORY_LAUNCHER)
                && getIntent().getAction() != null
                && getIntent().getAction().equals(Intent.ACTION_MAIN)) {

            finish();
            return;
        }

        if (savedInstanceState == null) {
            if (getIntent().hasCategory(Intent.CATEGORY_LAUNCHER)) {
                SystemClock.sleep(1500);
            }

            if (getIntent().getBooleanExtra(ARG_SHOW_LOGIN, false)) {
                login();
            }
        }

        setTheme(R.style.AppThemeBase);
        setContentView(R.layout.container_layout);
    }


    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        if (intent.getBooleanExtra(ARG_SHOW_LOGIN, false)) {
            login();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (accountHoster.isLoggedIn()) {
            Fragment homeFragment = getSupportFragmentManager().findFragmentByTag(HomeFragment.TAG);
            if (homeFragment == null) {
                UiUtils.replaceFragment(getSupportFragmentManager(), new HomeFragment(), R.id.content_frame, HomeFragment.TAG);
            }
        } else {
            Fragment loginRegisterFragment = getSupportFragmentManager().findFragmentByTag(LoginRegisterFragment.TAG);
            if (loginRegisterFragment == null) {
                UiUtils.replaceFragment(getSupportFragmentManager(), new LoginRegisterFragment(), R.id.content_frame, LoginRegisterFragment.TAG);
            }
        }
    }
}

{% endhighlight %}

## References

[How to prevent multiple instances of an activity when it is launched with different intents](https://stackoverflow.com/questions/4341600/how-to-prevent-multiple-instances-of-an-activity-when-it-is-launched-with-differ/7748416)
