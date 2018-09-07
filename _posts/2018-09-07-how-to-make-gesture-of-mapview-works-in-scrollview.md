---
title: How to make gesture of mapview works in scrollview
layout: post
date: 2018-09-07 05:09:42 +0800
categories: android
---

Customize scrollview to disable touch events in MapView rect.

{% highlight java %}

public final class MapScrollView extends ScrollView {
    private View touchView;
    private final Rect rect = new Rect();

    public MapScrollView(Context context) {
        this(context, null);
    }

    public MapScrollView(Context context, AttributeSet attrs) {
        super(context, attrs);
    }

    @Override
    protected void onFinishInflate() {
        super.onFinishInflate();
        touchView = findViewById(R.id.map_view);
    }

    @Override
    public boolean onInterceptTouchEvent(MotionEvent ev) {
        final int action = ev.getAction();
        final int actionMasked = action & MotionEvent.ACTION_MASK;
        if (actionMasked == MotionEvent.ACTION_DOWN) {
            int x = (int) ev.getRawX();
            int y = (int) ev.getRawY();
            touchView.getGlobalVisibleRect(rect);
            if (rect.contains(x, y)) {
                return false;
            }
        }
        return super.onInterceptTouchEvent(ev);
    }
}

{% endhighlight %}
