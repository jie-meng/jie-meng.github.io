---
title: Android account manager
layout: post
date: 2018-02-04 09:48:56 +0800
categories: android
---

## Account Model

First you need to have an account model which holds user information, let's create a simple model class: User.

{% highlight java %}

public class User implements Parcelable {

    @SerializedName("username")
    String username;

    @SerializedName("nickname")
    String nickname;

    @SerializedName("password")
    String password;

    @SerializedName("email")
    String email;

    @SerializedName("mobile_number")
    String mobileNumber;

    @SerializedName("access_token")
    String accessToken;

    public User() {
    }

    protected User(Parcel in) {
        username = in.readString();
        nickname = in.readString();
        password = in.readString();
        email = in.readString();
        mobileNumber = in.readString();
        accessToken = in.readString();
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeString(username);
        dest.writeString(nickname);
        dest.writeString(password);
        dest.writeString(email);
        dest.writeString(mobileNumber);
        dest.writeString(accessToken);
    }

    @Override
    public int describeContents() {
        return 0;
    }

    public static final Creator<User> CREATOR = new Creator<User>() {
        @Override
        public User createFromParcel(Parcel in) {
            return new User(in);
        }

        @Override
        public User[] newArray(int size) {
            return new User[size];
        }
    };

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getNickname() {
        return nickname;
    }

    public void setNickname(String nickname) {
        this.nickname = nickname;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getMobileNumber() {
        return mobileNumber;
    }

    public void setMobileNumber(String mobileNumber) {
        this.mobileNumber = mobileNumber;
    }

    public String getAccessToken() {
        return accessToken;
    }

    public void setAccessToken(String accessToken) {
        this.accessToken = accessToken;
    }
}

{% endhighlight %}

## Add permissions

The second thing you need to do is declare uses-permissions in Manifest.

{% highlight xml %}

<uses-permission android:name="android.permission.AUTHENTICATE_ACCOUNTS" />
<uses-permission android:name="android.permission.MANAGE_ACCOUNTS" />
<uses-permission android:name="android.permission.GET_ACCOUNTS" />

{% endhighlight %}

## Implement Authenticator

Then you need to extend the AbstractAccountAuthenticator and implement its methods to create our Authenticator.

You may decide to implement all the methods, or just leave out some by having them throw an UnsupportedOperationException. 

But at least need to implement the addAccount method to allow users to add an account in the system.

You also need to implement getAuthToken method if you want to support Authentication.

{% highlight java %}

public class AccountAuthenticator extends AbstractAccountAuthenticator {

    static final String KEY_ACCESS_TOKEN = "key_access_token";
    static final String KEY_USERNAME = "key_username";
    static final String KEY_NICKNAME = "key_nickname";
    static final String KEY_EMAIL = "key_email";
    static final String KEY_MOBILE_NUMBER = "key_mobile_number";

    private Context context;

    public AccountAuthenticator(Context context) {
        super(context);
        this.context = context;
    }

    @Override
    public Bundle editProperties(AccountAuthenticatorResponse response, String accountType) {
        throw new UnsupportedOperationException();
    }

    @Override
    public Bundle addAccount(AccountAuthenticatorResponse response, String accountType, String authTokenType, String[] requiredFeatures, Bundle options) throws NetworkErrorException {
        Bundle result = new Bundle();

        Intent intent = new Intent(context.getApplicationContext(), LoginActivity.class);
        intent.putExtra(AccountManager.KEY_ACCOUNT_MANAGER_RESPONSE, response);
        intent.putExtra(LoginActivity.ARG_DO_REGISTER, options.getBoolean(LoginActivity.ARG_DO_REGISTER));
        result.putParcelable(AccountManager.KEY_INTENT, intent);
        return result;
    }

    @Override
    public Bundle confirmCredentials(AccountAuthenticatorResponse response, Account account, Bundle options) throws NetworkErrorException {
        throw new UnsupportedOperationException();
    }

    @Override
    public Bundle getAuthToken(AccountAuthenticatorResponse response, Account account, String authTokenType, Bundle options) throws NetworkErrorException {
        Bundle result = new Bundle();
        String token = AccountManager.get(context).getUserData(account, KEY_ACCESS_TOKEN);
        result.putString(AccountManager.KEY_ACCOUNT_NAME, account.name);
        result.putString(AccountManager.KEY_ACCOUNT_TYPE, account.type);
        result.putString(AccountManager.KEY_AUTHTOKEN, token);
        return result;
    }

    @Override
    public String getAuthTokenLabel(String authTokenType) {
        throw new UnsupportedOperationException();
    }

    @Override
    public Bundle updateCredentials(AccountAuthenticatorResponse response, Account account, String authTokenType, Bundle options) throws NetworkErrorException {
        throw new UnsupportedOperationException();
    }

    @Override
    public Bundle hasFeatures(AccountAuthenticatorResponse response, Account account, String[] features) throws NetworkErrorException {
        throw new UnsupportedOperationException();
    }
}

{% endhighlight %}

## Build the Authentication Service

We have to define an AuthenticatorService and register it in the Manifest file with special filter and meta-data.

{% highlight java %}

public class AuthenticatorService extends Service {

    private AccountAuthenticator authenticator;

    @Override
    public void onCreate() {
        authenticator = new AccountAuthenticator(this);
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return authenticator.getIBinder();
    }
}

{% endhighlight %}

Then declare the service in Manifest:

{% highlight xml %}

<service
    android:name=".hosters.account_hoster.AuthenticatorService"
    android:enabled="true"
    android:exported="true">
    <intent-filter>
        <action android:name="android.accounts.AccountAuthenticator" />
    </intent-filter>

    <meta-data
        android:name="android.accounts.AccountAuthenticator"
        android:resource="@xml/authenticator" />
</service>

{% endhighlight %}

If you notice the meta-data tag there, you'll find android:resource's value something which hasn't been defined before. This xml file is important because it lets the system know how to represent your app in the settings.

Create a folder named xml in the res folder. In that folder, make a new file named authenticator.xml (name can be anything, as long as you specify it in the Manifest file). The contents of that file for my project looks like this

{% highlight xml %}

<?xml version="1.0" encoding="utf-8"?>
<account-authenticator xmlns:android="http://schemas.android.com/apk/res/android"
    android:accountType="@string/account_type"
    android:icon="@drawable/ic_launcher"
    android:label="@string/app_name"
    android:smallIcon="@drawable/ic_launcher" />

{% endhighlight %}

## Create AccountHoster

AccountHoster is a Singleton class which provide account managment interface to business logic.

{% highlight java %}

public class AccountHoster {
    private final AccountManager accountManager;
    private final String accountType;
    private User user;

    public AccountHoster(Context context) {
        this.accountManager = AccountManager.get(context);
        this.accountType = context.getString(R.string.account_type);
    }

    public void startLogin(Activity activity, boolean doRegister) {
        Bundle options = new Bundle();
        options.putBoolean(LoginActivity.ARG_DO_REGISTER, doRegister);
        accountManager.addAccount(accountType, null, null, options, activity, null, null);
    }

    public void saveAccount(User user, boolean persistent) {
        deleteAccount();
        if (persistent) {
            Account account = new Account(user.getUsername(), accountType);
            Bundle userdata = new Bundle();
            userdata.putString(AccountAuthenticator.KEY_ACCESS_TOKEN, user.getAccessToken());
            userdata.putString(AccountAuthenticator.KEY_USERNAME, user.getUsername());
            userdata.putString(AccountAuthenticator.KEY_NICKNAME, user.getNickname());
            userdata.putString(AccountAuthenticator.KEY_EMAIL, user.getEmail());
            userdata.putString(AccountAuthenticator.KEY_MOBILE_NUMBER, user.getMobileNumber());
            accountManager.addAccountExplicitly(account, user.getPassword(), userdata);
        } else {
            this.user = user;
        }
    }

    public void deleteAccount() {
        this.user = null;
        Account[] accounts = accountManager.getAccountsByType(accountType);
        for (Account account : accounts) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP_MR1) {
                accountManager.removeAccountExplicitly(account);
            } else {
                accountManager.removeAccount(account, null, null);
            }
        }
    }

    public boolean isLoggedIn() {
        return accountManager.getAccountsByType(accountType).length > 0;
    }

    public void updateAccount(User user) {
        if (isLoggedIn()) {
            Account account = accountManager.getAccountsByType(accountType)[0];
            accountManager.setUserData(account, AccountAuthenticator.KEY_USERNAME, user.getUsername());
            accountManager.setUserData(account, AccountAuthenticator.KEY_NICKNAME, user.getNickname());
            accountManager.setUserData(account, AccountAuthenticator.KEY_EMAIL, user.getEmail());
            accountManager.setUserData(account, AccountAuthenticator.KEY_MOBILE_NUMBER, user.getMobileNumber());
        }
    }

    public void updateAccountAccessToken(String accessToken) {
        if (isLoggedIn()) {
            Account account = accountManager.getAccountsByType(accountType)[0];
            accountManager.setUserData(account, AccountAuthenticator.KEY_ACCESS_TOKEN, accessToken);
        } else if (user != null) {
            user.setAccessToken(accessToken);
        }
    }

    public User getAccount() {
        if (isLoggedIn()) {
            User user = new User();
            Account account = accountManager.getAccountsByType(accountType)[0];
            user.setUsername(accountManager.getUserData(account, AccountAuthenticator.KEY_USERNAME));
            user.setNickname(accountManager.getUserData(account, AccountAuthenticator.KEY_NICKNAME));
            user.setEmail(accountManager.getUserData(account, AccountAuthenticator.KEY_EMAIL));
            user.setMobileNumber(accountManager.getUserData(account, AccountAuthenticator.KEY_MOBILE_NUMBER));

            return user;
        } else {
            return null;
        }
    }

    public String getAuthToken() {
        String token = null;
        if (isLoggedIn()) {
            try {
                token = accountManager.getUserData(accountManager.getAccountsByType(accountType)[0], AccountAuthenticator.KEY_ACCESS_TOKEN);
            } catch (Exception e) {
                e.printStackTrace();
            }
        } else if (user != null) {
            token = user.getAccessToken();
        }
        return token;
    }
}

{% endhighlight %}

## References

[Android Account Manager: Introduction and Basic Implementation](https://www.pilanites.com/android-account-manager)

[Write your own Android Authenticator](http://blog.udinic.com/2013/04/24/write-your-own-android-authenticator)
