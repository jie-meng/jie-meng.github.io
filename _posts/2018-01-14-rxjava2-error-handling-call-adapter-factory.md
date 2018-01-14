---
title: RxJava2 Error Handling CallAdapterFactory
layout: post
date: '2018-01-14 12:06:00 +0800'
categories: android
---

First, Create a subclass of CallAdapter.Factory

{% highlight java %}

public class RxErrorHandlingCallAdapterFactory extends CallAdapter.Factory {
    private final RxJava2CallAdapterFactory original;
    private final Gson gson;

    private RxErrorHandlingCallAdapterFactory(RxJava2CallAdapterFactory original, Gson gson) {
        this.original = original;
        this.gson = gson;
    }

    public static CallAdapter.Factory create(RxJava2CallAdapterFactory original, Gson gson) {
        return new RxErrorHandlingCallAdapterFactory(original, gson);
    }

    @Override
    public CallAdapter<?, ?> get(@android.support.annotation.NonNull Type returnType,
                                 @android.support.annotation.NonNull Annotation[] annotations,
                                 @android.support.annotation.NonNull Retrofit retrofit) {
        CallAdapter<?, ?> callAdapter = original.get(returnType, annotations, retrofit);
        return new RxCallAdapterWrapper(gson, returnType, callAdapter);
    }

    private static class RxCallAdapterWrapper<R> implements CallAdapter<R, Object> {
        private final Gson gson;
        private final CallAdapter<R, Object> wrapped;

        private final boolean isObservable;
        private final boolean isFlowable;
        private final boolean isSingle;
        private final boolean isMaybe;
        private final boolean isCompletable;

        @SuppressWarnings("unchecked")
        RxCallAdapterWrapper(Gson gson, Type returnType, CallAdapter wrapped) {
            this.gson = gson;
            Class<?> rawType = getRawType(returnType);
            this.isObservable = rawType == Observable.class;
            this.isFlowable = rawType == Flowable.class;
            this.isSingle = rawType == Single.class;
            this.isMaybe = rawType == Maybe.class;
            this.isCompletable = rawType == Completable.class;
            this.wrapped = (CallAdapter<R, Object>) wrapped;
        }

        @Override
        public Type responseType() {
            return wrapped.responseType();
        }

        @Override
        @SuppressWarnings("unchecked")
        public Object adapt(@android.support.annotation.NonNull Call<R> call) {
            Object object = wrapped.adapt(call);

            if (isObservable) {
                return ((Observable) object).onErrorResumeNext(new Function<Throwable, ObservableSource>() {
                    @Override
                    public ObservableSource apply(@NonNull Throwable throwable) throws Exception {
                        return Observable.error(asRetrofitException(throwable));
                    }
                });
            }

            if (isFlowable) {
                return ((Flowable) object).onErrorResumeNext(new Function<Throwable, Publisher>() {
                    @Override
                    public Publisher apply(@NonNull Throwable throwable) throws Exception {
                        return Flowable.error(asRetrofitException(throwable));
                    }
                });
            }

            if (isSingle) {
                return ((Single) object).onErrorResumeNext(new Function<Throwable, SingleSource>() {
                    @Override
                    public SingleSource apply(@NonNull Throwable throwable) throws Exception {
                        return Single.error(asRetrofitException(throwable));
                    }
                });
            }

            if (isMaybe) {
                return ((Maybe) object).onErrorResumeNext(new Function<Throwable, MaybeSource>() {
                    @Override
                    public MaybeSource apply(@NonNull Throwable throwable) throws Exception {
                        return Maybe.error(asRetrofitException(throwable));
                    }
                });
            }

            if (isCompletable) {
                return ((Completable) object).onErrorResumeNext(new Function<Throwable, CompletableSource>() {
                    @Override
                    public Completable apply(@NonNull Throwable throwable) throws Exception {
                        return new CompletableError(asRetrofitException(throwable));
                    }
                });
            }

            return null;
        }

        private Throwable asRetrofitException(Throwable throwable) {
            if (throwable instanceof HttpException) {
                HttpException httpException = (HttpException) throwable;
                Response response = httpException.response();
                return RemoteException.httpError(response.raw().request().url().toString(), response, throwable, gson);
            }

            return throwable;
        }


        private static Class<?> getRawType(Type type) {
            if (type == null) {
                throw new IllegalArgumentException("type == null");
            }

            if (type instanceof Class<?>) {
                // Type is a normal class.
                return (Class<?>) type;
            }
            if (type instanceof ParameterizedType) {
                ParameterizedType parameterizedType = (ParameterizedType) type;

                // I'm not exactly sure why getRawType() returns Type instead of Class. Neal isn't either but
                // suspects some pathological case related to nested classes exists.
                Type rawType = parameterizedType.getRawType();
                if (!(rawType instanceof Class)) throw new IllegalArgumentException();
                return (Class<?>) rawType;
            }
            if (type instanceof GenericArrayType) {
                Type componentType = ((GenericArrayType) type).getGenericComponentType();
                return Array.newInstance(getRawType(componentType), 0).getClass();
            }
            if (type instanceof TypeVariable) {
                // We could use the variable's bounds, but that won't work if there are multiple. Having a raw
                // type that's more general than necessary is okay.
                return Object.class;
            }
            if (type instanceof WildcardType) {
                return getRawType(((WildcardType) type).getUpperBounds()[0]);
            }

            throw new IllegalArgumentException("Expected a Class, ParameterizedType, or "
                    + "GenericArrayType, but <" + type + "> is of type " + type.getClass().getName());
        }
    }
}

{% endhighlight %}

Then use it as

{% highlight java %}

public Retrofit provideRetrofit(Gson gson, OkHttpClient okHttpClient) {
    return new Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .addCallAdapterFactory(RxErrorHandlingCallAdapterFactory.create(RxJava2CallAdapterFactory.create(), gson))
            .build();
}

{% endhighlight %}

## References

[Retrofit 2 and Rx Java call adapter error handling](https://bytes.babbel.com/en/articles/2016-03-16-retrofit2-rxjava-error-handling.html)
