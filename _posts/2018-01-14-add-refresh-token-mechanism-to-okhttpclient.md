---
title: Add refresh token mechanism to OkHttpClient
layout: post
date: 2018-01-14 01:22:44 +0800
categories: android
---

When Android app communicate with server via http, sometimes you need an AccessToken and a RefreshToken.

After you login, you got an AccessToken and a RefreshToken, Then you can make your common request with AccessToken, 

If server gives you a response with code 401(UNAUTHORIZED), That means your AccessToken can not be used any more, that may caused by another user login with your account, or AccessToken expired.

Then you should retrieve a new AccessToken with you RefreshToken.

Here shows the code of refresh token on OkHttpClient via its Interceptor mechanism.

{% highlight java %}

public class RefreshTokenInterceptor implements Interceptor {

    private static final String HTTP_HEADER_ACCEPT = "Accept";
    private static final String HTTP_HEADER_CONTENT_TYPE = "Content-Type";
    private static final String HTTP_HEADER_AUTHORIZATION = "ACCESS-AUTH-TOKEN";
    private static final String HTTP_HEADER_CLIENT_ID = "CLIENT-ID";

    private AccountUtil accountUtil;
    private Gson gson;
    private String baseUrl;

    public RefreshTokenInterceptor(AccountUtil accountUtil, Gson gson, String baseUrl) {
        this.accountUtil = accountUtil;
        this.gson = gson;
        this.baseUrl = baseUrl;
    }

    @Override
    public Response intercept(Chain chain) throws IOException {
        Request request = buildRequest(accountUtil, chain);
        okhttp3.Response response = chain.proceed(request);
        if (response.code() != HttpResponseCode.UNAUTHORIZED || !accountUtil.isLoggedIn()) {
            return response;
        }

        okhttp3.Response refreshTokenResponse = refreshToken(accountUtil, gson, chain);
        if (refreshTokenResponse.code() == HttpResponseCode.OK) {
            Type type = new TypeToken<Response<RefreshTokenResponse>>() {
            }.getType();
            String accessToken = ((Response<RefreshTokenResponse>) gson.fromJson(refreshTokenResponse.body().string(), type))
                    .getData().getAccessToken();
            accountUtil.updateAccountAccessToken(accessToken);
            request = buildRequest(accountUtil, chain);
            return chain.proceed(request);
        } else {
            return refreshTokenResponse;
        }
    }

    private okhttp3.Response refreshToken(AccountUtil accountUtil, Gson gson, Interceptor.Chain chain) throws IOException {
        Request.Builder builder = new Request.Builder()
                .url(baseUrl + "/user/refresh_token")
                .addHeader(HTTP_HEADER_CONTENT_TYPE, "application/json")
                .addHeader(HTTP_HEADER_ACCEPT, "application/json")
                .post(RequestBody.create(MediaType.parse("application/json; charset=utf-8"),
                        gson.toJson(new RefreshTokenRequest(accountUtil.getAuthToken(), accountUtil.getClientId(), accountUtil.getRefreshToken()))));

        return chain.proceed(builder.build());
    }

    private Request buildRequest(AccountUtil accountUtil, Interceptor.Chain chain) {
        String authToken = accountUtil.getAuthToken();
        String clientId = accountUtil.getClientId();
        Request.Builder builder = chain.request().newBuilder()
                .addHeader(HTTP_HEADER_CONTENT_TYPE, "application/json")
                .addHeader(HTTP_HEADER_ACCEPT, "application/json")
                .addHeader(HTTP_HEADER_AUTHORIZATION, authToken == null ? "" : authToken)
                .addHeader(HTTP_HEADER_CLIENT_ID, clientId == null ? "" : clientId);

        return builder.build();
    }
}

{% endhighlight %}

Then add this interceptor to your OkHttpClient.

{% highlight java %}

public OkHttpClient provideOkHttpClient(final AccountUtil accountUtil, final Gson gson) {
    HttpLoggingInterceptor httpLoggingInterceptor = new HttpLoggingInterceptor(message -> Timber.v(message));
    httpLoggingInterceptor.setLevel(HttpLoggingInterceptor.Level.BODY);
    return new OkHttpClient.Builder()
            .addInterceptor(new RefreshTokenInterceptor(accountUtil, gson, baseUrl))
            .addInterceptor(httpLoggingInterceptor)
            .connectTimeout(TIME_OUT, TimeUnit.SECONDS)
            .readTimeout(TIME_OUT, TimeUnit.SECONDS)
            .writeTimeout(TIME_OUT, TimeUnit.SECONDS)
            .build();
}
                
{% endhighlight %}                
                