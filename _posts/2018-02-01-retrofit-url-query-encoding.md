---
title: Retrofit URL query encoding
layout: post
date: 2018-02-01 11:07:47 +0800
categories: android
---

When you call restful API with Retrofit, sometimes there are query arguments which are JSON objects you should provide. 

The json format string contains characters which cannot be used in a URL such as quotation, comma ...

Then we have to do encoding on the JSON objects to fit URL format.

First of all, you got an API contract:

{% highlight java %}
private interface SomeApi {
    @GET("user/{user_id}/cards")
    Single<Response<List<Card>>> getCards(@Path("user_id") String userId, @Query(value = "query", encoded = true) Filter filter);
}
{% endhighlight %}

We need to get cards of a user based on a filter. The query argument which marked as @Query would appear in the request URL. But it's not a builtin type such as int, String ...

It's a Java object which would be turned in to a JSON string then pass to the request URL. So we have to encode it.

{% highlight java %}

public final class EncodingGsonConverterFactory extends Converter.Factory {
    public static EncodingGsonConverterFactory create(GsonConverterFactory gsonConverterFactory, Gson gson) {
        if (gsonConverterFactory == null)
            throw new NullPointerException("gsonConverterFactory == null");
        if (gson == null) throw new NullPointerException("gson == null");
        return new EncodingGsonConverterFactory(gsonConverterFactory, gson);
    }

    private final GsonConverterFactory gsonConverterFactory;
    private final Gson gson;


    private EncodingGsonConverterFactory(GsonConverterFactory gsonConverterFactory, Gson gson) {
        this.gsonConverterFactory = gsonConverterFactory;
        this.gson = gson;
    }

    @Nullable
    @Override
    public Converter<?, String> stringConverter(Type type, Annotation[] annotations, Retrofit retrofit) {
        return (Converter<Object, String>) value -> {
            if (value instanceof CharSequence || value instanceof Boolean || value instanceof Character || value instanceof Number)
                return value.toString();
            return URLEncoder.encode(gson.toJson(value), "UTF-8");
        };
    }

    @Override
    public Converter<ResponseBody, ?> responseBodyConverter(Type type, Annotation[] annotations,
                                                            Retrofit retrofit) {
        return gsonConverterFactory.responseBodyConverter(type, annotations, retrofit);
    }

    @Override
    public Converter<?, RequestBody> requestBodyConverter(Type type,
                                                          Annotation[] parameterAnnotations, Annotation[] methodAnnotations, Retrofit retrofit) {
        return gsonConverterFactory.requestBodyConverter(type, parameterAnnotations, methodAnnotations, retrofit);
    }
}

{% endhighlight %}

Then add the EncodingGsonConverterFactory to your Retrofit instance.

{% highlight java %}

public Retrofit provideRetrofit(Gson gson, OkHttpClient okHttpClient) {
    return new Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(okHttpClient)
            .addConverterFactory(EncodingGsonConverterFactory.create(GsonConverterFactory.create(gson), gson))
            .build();
}

{% endhighlight %}
