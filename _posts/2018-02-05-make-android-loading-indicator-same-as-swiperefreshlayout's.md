---
title: Make Android Loading Indicator same as SwipeRefreshLayout's
layout: post
date: 2018-02-05 09:17:06 +0800
categories: android
---

Loading indicator of SwipeRefreshLayout can be used when we do network request and waiting for response. But CircleImageView of SwipeRefreshLayout is an internal class of android.support.v4.widget.

So we need to make a copy of CircleImageView.

{% highlight java %}

public class CircleImageView extends android.support.v7.widget.AppCompatImageView {

    private static final int KEY_SHADOW_COLOR = 0x1E000000;
    private static final int FILL_SHADOW_COLOR = 0x3D000000;
    // PX
    private static final float X_OFFSET = 0f;
    private static final float Y_OFFSET = 1.75f;
    private static final float SHADOW_RADIUS = 3.5f;
    private static final int SHADOW_ELEVATION = 4;

    private Animation.AnimationListener mListener;
    int mShadowRadius;

    CircleImageView(Context context, int color) {
        super(context);
        final float density = getContext().getResources().getDisplayMetrics().density;
        final int shadowYOffset = (int) (density * Y_OFFSET);
        final int shadowXOffset = (int) (density * X_OFFSET);

        mShadowRadius = (int) (density * SHADOW_RADIUS);

        ShapeDrawable circle;
        if (elevationSupported()) {
            circle = new ShapeDrawable(new OvalShape());
            ViewCompat.setElevation(this, SHADOW_ELEVATION * density);
        } else {
            OvalShape oval = new CircleImageView.OvalShadow(mShadowRadius);
            circle = new ShapeDrawable(oval);
            setLayerType(View.LAYER_TYPE_SOFTWARE, circle.getPaint());
            circle.getPaint().setShadowLayer(mShadowRadius, shadowXOffset, shadowYOffset,
                    KEY_SHADOW_COLOR);
            final int padding = mShadowRadius;
            // set padding so the inner image sits correctly within the shadow.
            setPadding(padding, padding, padding, padding);
        }
        circle.getPaint().setColor(color);
        ViewCompat.setBackground(this, circle);
    }

    private boolean elevationSupported() {
        return android.os.Build.VERSION.SDK_INT >= 21;
    }

    @Override
    protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
        super.onMeasure(widthMeasureSpec, heightMeasureSpec);
        if (!elevationSupported()) {
            setMeasuredDimension(getMeasuredWidth() + mShadowRadius * 2, getMeasuredHeight()
                    + mShadowRadius * 2);
        }
    }

    public void setAnimationListener(Animation.AnimationListener listener) {
        mListener = listener;
    }

    @Override
    public void onAnimationStart() {
        super.onAnimationStart();
        if (mListener != null) {
            mListener.onAnimationStart(getAnimation());
        }
    }

    @Override
    public void onAnimationEnd() {
        super.onAnimationEnd();
        if (mListener != null) {
            mListener.onAnimationEnd(getAnimation());
        }
    }

    public void setBackgroundColorRes(int colorRes) {
        setBackgroundColor(ContextCompat.getColor(getContext(), colorRes));
    }

    @Override
    public void setBackgroundColor(int color) {
        if (getBackground() instanceof ShapeDrawable) {
            ((ShapeDrawable) getBackground()).getPaint().setColor(color);
        }
    }

    private class OvalShadow extends OvalShape {
        private RadialGradient mRadialGradient;
        private Paint mShadowPaint;

        OvalShadow(int shadowRadius) {
            super();
            mShadowPaint = new Paint();
            mShadowRadius = shadowRadius;
            updateRadialGradient((int) rect().width());
        }

        @Override
        protected void onResize(float width, float height) {
            super.onResize(width, height);
            updateRadialGradient((int) width);
        }

        @Override
        public void draw(Canvas canvas, Paint paint) {
            final int viewWidth = CircleImageView.this.getWidth();
            final int viewHeight = CircleImageView.this.getHeight();
            canvas.drawCircle(viewWidth / 2, viewHeight / 2, viewWidth / 2, mShadowPaint);
            canvas.drawCircle(viewWidth / 2, viewHeight / 2, viewWidth / 2 - mShadowRadius, paint);
        }

        private void updateRadialGradient(int diameter) {
            mRadialGradient = new RadialGradient(diameter / 2, diameter / 2,
                    mShadowRadius, new int[]{FILL_SHADOW_COLOR, Color.TRANSPARENT},
                    null, Shader.TileMode.CLAMP);
            mShadowPaint.setShader(mRadialGradient);
        }
    }
}

{% endhighlight %}

Then MaterialProgressDrawable which shows animation.

{% highlight java %}

// Fancy progress indicator for Material theme.
class MaterialProgressDrawable extends Drawable implements Animatable {
    private static final Interpolator LINEAR_INTERPOLATOR = new LinearInterpolator();
    static final Interpolator MATERIAL_INTERPOLATOR = new FastOutSlowInInterpolator();

    private static final float FULL_ROTATION = 1080.0f;

    @Retention(RetentionPolicy.SOURCE)
    @IntDef({LARGE, DEFAULT})
    public @interface ProgressDrawableSize {}

    // Maps to ProgressBar.Large style
    static final int LARGE = 0;
    // Maps to ProgressBar default style
    static final int DEFAULT = 1;

    // Maps to ProgressBar default style
    private static final int CIRCLE_DIAMETER = 40;
    private static final float CENTER_RADIUS = 8.75f; //should add up to 10 when + stroke_width
    private static final float STROKE_WIDTH = 2.5f;

    // Maps to ProgressBar.Large style
    private static final int CIRCLE_DIAMETER_LARGE = 56;
    private static final float CENTER_RADIUS_LARGE = 12.5f;
    private static final float STROKE_WIDTH_LARGE = 3f;

    private static final int[] COLORS = new int[] {
            Color.BLACK
    };

    private static final float COLOR_START_DELAY_OFFSET = 0.75f;
    private static final float END_TRIM_START_DELAY_OFFSET = 0.5f;
    private static final float START_TRIM_DURATION_OFFSET = 0.5f;

    private static final int ANIMATION_DURATION = 1332;

    private static final float NUM_POINTS = 5f;

    private final ArrayList<Animation> mAnimators = new ArrayList<Animation>();

    private final Ring mRing;

    private float mRotation;

    private static final int ARROW_WIDTH = 10;
    private static final int ARROW_HEIGHT = 5;
    private static final float ARROW_OFFSET_ANGLE = 5;

    private static final int ARROW_WIDTH_LARGE = 12;
    private static final int ARROW_HEIGHT_LARGE = 6;
    private static final float MAX_PROGRESS_ARC = .8f;

    private Resources mResources;
    private View mParent;
    private Animation mAnimation;
    float mRotationCount;
    private double mWidth;
    private double mHeight;
    boolean mFinishing;

    MaterialProgressDrawable(Context context, View parent) {
        mParent = parent;
        mResources = context.getResources();

        mRing = new Ring(mCallback);
        mRing.setColors(COLORS);

        updateSizes(DEFAULT);
        setupAnimators();
    }

    private void setSizeParameters(double progressCircleWidth, double progressCircleHeight,
                                   double centerRadius, double strokeWidth, float arrowWidth, float arrowHeight) {
        final Ring ring = mRing;
        final DisplayMetrics metrics = mResources.getDisplayMetrics();
        final float screenDensity = metrics.density;

        mWidth = progressCircleWidth * screenDensity;
        mHeight = progressCircleHeight * screenDensity;
        ring.setStrokeWidth((float) strokeWidth * screenDensity);
        ring.setCenterRadius(centerRadius * screenDensity);
        ring.setColorIndex(0);
        ring.setArrowDimensions(arrowWidth * screenDensity, arrowHeight * screenDensity);
        ring.setInsets((int) mWidth, (int) mHeight);
    }

    public void updateSizes(@ProgressDrawableSize int size) {
        if (size == LARGE) {
            setSizeParameters(CIRCLE_DIAMETER_LARGE, CIRCLE_DIAMETER_LARGE, CENTER_RADIUS_LARGE,
                    STROKE_WIDTH_LARGE, ARROW_WIDTH_LARGE, ARROW_HEIGHT_LARGE);
        } else {
            setSizeParameters(CIRCLE_DIAMETER, CIRCLE_DIAMETER, CENTER_RADIUS, STROKE_WIDTH,
                    ARROW_WIDTH, ARROW_HEIGHT);
        }
    }

    public void showArrow(boolean show) {
        mRing.setShowArrow(show);
    }

    public void setArrowScale(float scale) {
        mRing.setArrowScale(scale);
    }

    public void setStartEndTrim(float startAngle, float endAngle) {
        mRing.setStartTrim(startAngle);
        mRing.setEndTrim(endAngle);
    }

    public void setProgressRotation(float rotation) {
        mRing.setRotation(rotation);
    }

    public void setBackgroundColor(int color) {
        mRing.setBackgroundColor(color);
    }

    public void setColorSchemeColors(int... colors) {
        mRing.setColors(colors);
        mRing.setColorIndex(0);
    }

    @Override
    public int getIntrinsicHeight() {
        return (int) mHeight;
    }

    @Override
    public int getIntrinsicWidth() {
        return (int) mWidth;
    }

    @Override
    public void draw(Canvas c) {
        final Rect bounds = getBounds();
        final int saveCount = c.save();
        c.rotate(mRotation, bounds.exactCenterX(), bounds.exactCenterY());
        mRing.draw(c, bounds);
        c.restoreToCount(saveCount);
    }

    @Override
    public void setAlpha(int alpha) {
        mRing.setAlpha(alpha);
    }

    public int getAlpha() {
        return mRing.getAlpha();
    }

    @Override
    public void setColorFilter(ColorFilter colorFilter) {
        mRing.setColorFilter(colorFilter);
    }

    @SuppressWarnings("unused")
    void setRotation(float rotation) {
        mRotation = rotation;
        invalidateSelf();
    }

    @SuppressWarnings("unused")
    private float getRotation() {
        return mRotation;
    }

    @Override
    public int getOpacity() {
        return PixelFormat.TRANSLUCENT;
    }

    @Override
    public boolean isRunning() {
        final ArrayList<Animation> animators = mAnimators;
        final int N = animators.size();
        for (int i = 0; i < N; i++) {
            final Animation animator = animators.get(i);
            if (animator.hasStarted() && !animator.hasEnded()) {
                return true;
            }
        }
        return false;
    }

    @Override
    public void start() {
        mAnimation.reset();
        mRing.storeOriginals();
        // Already showing some part of the ring
        if (mRing.getEndTrim() != mRing.getStartTrim()) {
            mFinishing = true;
            mAnimation.setDuration(ANIMATION_DURATION / 2);
            mParent.startAnimation(mAnimation);
        } else {
            mRing.setColorIndex(0);
            mRing.resetOriginals();
            mAnimation.setDuration(ANIMATION_DURATION);
            mParent.startAnimation(mAnimation);
        }
    }

    @Override
    public void stop() {
        mParent.clearAnimation();
        setRotation(0);
        mRing.setShowArrow(false);
        mRing.setColorIndex(0);
        mRing.resetOriginals();
    }

    float getMinProgressArc(Ring ring) {
        return (float) Math.toRadians(
                ring.getStrokeWidth() / (2 * Math.PI * ring.getCenterRadius()));
    }

    // Adapted from ArgbEvaluator.java
    private int evaluateColorChange(float fraction, int startValue, int endValue) {
        int startInt = (Integer) startValue;
        int startA = (startInt >> 24) & 0xff;
        int startR = (startInt >> 16) & 0xff;
        int startG = (startInt >> 8) & 0xff;
        int startB = startInt & 0xff;

        int endInt = (Integer) endValue;
        int endA = (endInt >> 24) & 0xff;
        int endR = (endInt >> 16) & 0xff;
        int endG = (endInt >> 8) & 0xff;
        int endB = endInt & 0xff;

        return (int) ((startA + (int) (fraction * (endA - startA))) << 24)
                | (int) ((startR + (int) (fraction * (endR - startR))) << 16)
                | (int) ((startG + (int) (fraction * (endG - startG))) << 8)
                | (int) ((startB + (int) (fraction * (endB - startB))));
    }

    void updateRingColor(float interpolatedTime, Ring ring) {
        if (interpolatedTime > COLOR_START_DELAY_OFFSET) {
            // scale the interpolatedTime so that the full
            // transformation from 0 - 1 takes place in the
            // remaining time
            ring.setColor(evaluateColorChange((interpolatedTime - COLOR_START_DELAY_OFFSET)
                            / (1.0f - COLOR_START_DELAY_OFFSET), ring.getStartingColor(),
                    ring.getNextColor()));
        }
    }

    void applyFinishTranslation(float interpolatedTime, Ring ring) {
        // shrink back down and complete a full rotation before
        // starting other circles
        // Rotation goes between [0..1].
        updateRingColor(interpolatedTime, ring);
        float targetRotation = (float) (Math.floor(ring.getStartingRotation() / MAX_PROGRESS_ARC)
                + 1f);
        final float minProgressArc = getMinProgressArc(ring);
        final float startTrim = ring.getStartingStartTrim()
                + (ring.getStartingEndTrim() - minProgressArc - ring.getStartingStartTrim())
                * interpolatedTime;
        ring.setStartTrim(startTrim);
        ring.setEndTrim(ring.getStartingEndTrim());
        final float rotation = ring.getStartingRotation()
                + ((targetRotation - ring.getStartingRotation()) * interpolatedTime);
        ring.setRotation(rotation);
    }

    private void setupAnimators() {
        final Ring ring = mRing;
        final Animation animation = new Animation() {
            @Override
            public void applyTransformation(float interpolatedTime, Transformation t) {
                if (mFinishing) {
                    applyFinishTranslation(interpolatedTime, ring);
                } else {
                    // The minProgressArc is calculated from 0 to create an
                    // angle that matches the stroke width.
                    final float minProgressArc = getMinProgressArc(ring);
                    final float startingEndTrim = ring.getStartingEndTrim();
                    final float startingTrim = ring.getStartingStartTrim();
                    final float startingRotation = ring.getStartingRotation();

                    updateRingColor(interpolatedTime, ring);

                    // Moving the start trim only occurs in the first 50% of a
                    // single ring animation
                    if (interpolatedTime <= START_TRIM_DURATION_OFFSET) {
                        // scale the interpolatedTime so that the full
                        // transformation from 0 - 1 takes place in the
                        // remaining time
                        final float scaledTime = (interpolatedTime)
                                / (1.0f - START_TRIM_DURATION_OFFSET);
                        final float startTrim = startingTrim
                                + ((MAX_PROGRESS_ARC - minProgressArc) * MATERIAL_INTERPOLATOR
                                .getInterpolation(scaledTime));
                        ring.setStartTrim(startTrim);
                    }

                    // Moving the end trim starts after 50% of a single ring
                    // animation completes
                    if (interpolatedTime > END_TRIM_START_DELAY_OFFSET) {
                        // scale the interpolatedTime so that the full
                        // transformation from 0 - 1 takes place in the
                        // remaining time
                        final float minArc = MAX_PROGRESS_ARC - minProgressArc;
                        float scaledTime = (interpolatedTime - START_TRIM_DURATION_OFFSET)
                                / (1.0f - START_TRIM_DURATION_OFFSET);
                        final float endTrim = startingEndTrim
                                + (minArc * MATERIAL_INTERPOLATOR.getInterpolation(scaledTime));
                        ring.setEndTrim(endTrim);
                    }

                    final float rotation = startingRotation + (0.25f * interpolatedTime);
                    ring.setRotation(rotation);

                    float groupRotation = ((FULL_ROTATION / NUM_POINTS) * interpolatedTime)
                            + (FULL_ROTATION * (mRotationCount / NUM_POINTS));
                    setRotation(groupRotation);
                }
            }
        };
        animation.setRepeatCount(Animation.INFINITE);
        animation.setRepeatMode(Animation.RESTART);
        animation.setInterpolator(LINEAR_INTERPOLATOR);
        animation.setAnimationListener(new Animation.AnimationListener() {

            @Override
            public void onAnimationStart(Animation animation) {
                mRotationCount = 0;
            }

            @Override
            public void onAnimationEnd(Animation animation) {
                // do nothing
            }

            @Override
            public void onAnimationRepeat(Animation animation) {
                ring.storeOriginals();
                ring.goToNextColor();
                ring.setStartTrim(ring.getEndTrim());
                if (mFinishing) {
                    // finished closing the last ring from the swipe gesture; go
                    // into progress mode
                    mFinishing = false;
                    animation.setDuration(ANIMATION_DURATION);
                    ring.setShowArrow(false);
                } else {
                    mRotationCount = (mRotationCount + 1) % (NUM_POINTS);
                }
            }
        });
        mAnimation = animation;
    }

    private final Callback mCallback = new Callback() {
        @Override
        public void invalidateDrawable(Drawable d) {
            invalidateSelf();
        }

        @Override
        public void scheduleDrawable(Drawable d, Runnable what, long when) {
            scheduleSelf(what, when);
        }

        @Override
        public void unscheduleDrawable(Drawable d, Runnable what) {
            unscheduleSelf(what);
        }
    };

    private static class Ring {
        private final RectF mTempBounds = new RectF();
        private final Paint mPaint = new Paint();
        private final Paint mArrowPaint = new Paint();

        private final Callback mCallback;

        private float mStartTrim = 0.0f;
        private float mEndTrim = 0.0f;
        private float mRotation = 0.0f;
        private float mStrokeWidth = 5.0f;
        private float mStrokeInset = 2.5f;

        private int[] mColors;
        // mColorIndex represents the offset into the available mColors that the
        // progress circle should currently display. As the progress circle is
        // animating, the mColorIndex moves by one to the next available color.
        private int mColorIndex;
        private float mStartingStartTrim;
        private float mStartingEndTrim;
        private float mStartingRotation;
        private boolean mShowArrow;
        private Path mArrow;
        private float mArrowScale;
        private double mRingCenterRadius;
        private int mArrowWidth;
        private int mArrowHeight;
        private int mAlpha;
        private final Paint mCirclePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private int mBackgroundColor;
        private int mCurrentColor;

        Ring(Callback callback) {
            mCallback = callback;

            mPaint.setStrokeCap(Paint.Cap.SQUARE);
            mPaint.setAntiAlias(true);
            mPaint.setStyle(Style.STROKE);

            mArrowPaint.setStyle(Style.FILL);
            mArrowPaint.setAntiAlias(true);
        }

        public void setBackgroundColor(int color) {
            mBackgroundColor = color;
        }

        public void setArrowDimensions(float width, float height) {
            mArrowWidth = (int) width;
            mArrowHeight = (int) height;
        }

        public void draw(Canvas c, Rect bounds) {
            final RectF arcBounds = mTempBounds;
            arcBounds.set(bounds);
            arcBounds.inset(mStrokeInset, mStrokeInset);

            final float startAngle = (mStartTrim + mRotation) * 360;
            final float endAngle = (mEndTrim + mRotation) * 360;
            float sweepAngle = endAngle - startAngle;

            mPaint.setColor(mCurrentColor);
            c.drawArc(arcBounds, startAngle, sweepAngle, false, mPaint);

            drawTriangle(c, startAngle, sweepAngle, bounds);

            if (mAlpha < 255) {
                mCirclePaint.setColor(mBackgroundColor);
                mCirclePaint.setAlpha(255 - mAlpha);
                c.drawCircle(bounds.exactCenterX(), bounds.exactCenterY(), bounds.width() / 2,
                        mCirclePaint);
            }
        }

        private void drawTriangle(Canvas c, float startAngle, float sweepAngle, Rect bounds) {
            if (mShowArrow) {
                if (mArrow == null) {
                    mArrow = new Path();
                    mArrow.setFillType(Path.FillType.EVEN_ODD);
                } else {
                    mArrow.reset();
                }

                // Adjust the position of the triangle so that it is inset as
                // much as the arc, but also centered on the arc.
                float inset = (int) mStrokeInset / 2 * mArrowScale;
                float x = (float) (mRingCenterRadius * Math.cos(0) + bounds.exactCenterX());
                float y = (float) (mRingCenterRadius * Math.sin(0) + bounds.exactCenterY());

                // Update the path each time. This works around an issue in SKIA
                // where concatenating a rotation matrix to a scale matrix
                // ignored a starting negative rotation. This appears to have
                // been fixed as of API 21.
                mArrow.moveTo(0, 0);
                mArrow.lineTo(mArrowWidth * mArrowScale, 0);
                mArrow.lineTo((mArrowWidth * mArrowScale / 2), (mArrowHeight
                        * mArrowScale));
                mArrow.offset(x - inset, y);
                mArrow.close();
                // draw a triangle
                mArrowPaint.setColor(mCurrentColor);
                c.rotate(startAngle + sweepAngle - ARROW_OFFSET_ANGLE, bounds.exactCenterX(),
                        bounds.exactCenterY());
                c.drawPath(mArrow, mArrowPaint);
            }
        }

        public void setColors(@NonNull int[] colors) {
            mColors = colors;
            // if colors are reset, make sure to reset the color index as well
            setColorIndex(0);
        }

        public void setColor(int color) {
            mCurrentColor = color;
        }

        public void setColorIndex(int index) {
            mColorIndex = index;
            mCurrentColor = mColors[mColorIndex];
        }

        public int getNextColor() {
            return mColors[getNextColorIndex()];
        }

        private int getNextColorIndex() {
            return (mColorIndex + 1) % (mColors.length);
        }

        public void goToNextColor() {
            setColorIndex(getNextColorIndex());
        }

        public void setColorFilter(ColorFilter filter) {
            mPaint.setColorFilter(filter);
            invalidateSelf();
        }

        public void setAlpha(int alpha) {
            mAlpha = alpha;
        }

        public int getAlpha() {
            return mAlpha;
        }

        public void setStrokeWidth(float strokeWidth) {
            mStrokeWidth = strokeWidth;
            mPaint.setStrokeWidth(strokeWidth);
            invalidateSelf();
        }

        @SuppressWarnings("unused")
        public float getStrokeWidth() {
            return mStrokeWidth;
        }

        @SuppressWarnings("unused")
        public void setStartTrim(float startTrim) {
            mStartTrim = startTrim;
            invalidateSelf();
        }

        @SuppressWarnings("unused")
        public float getStartTrim() {
            return mStartTrim;
        }

        public float getStartingStartTrim() {
            return mStartingStartTrim;
        }

        public float getStartingEndTrim() {
            return mStartingEndTrim;
        }

        public int getStartingColor() {
            return mColors[mColorIndex];
        }

        @SuppressWarnings("unused")
        public void setEndTrim(float endTrim) {
            mEndTrim = endTrim;
            invalidateSelf();
        }

        @SuppressWarnings("unused")
        public float getEndTrim() {
            return mEndTrim;
        }

        @SuppressWarnings("unused")
        public void setRotation(float rotation) {
            mRotation = rotation;
            invalidateSelf();
        }

        @SuppressWarnings("unused")
        public float getRotation() {
            return mRotation;
        }

        public void setInsets(int width, int height) {
            final float minEdge = (float) Math.min(width, height);
            float insets;
            if (mRingCenterRadius <= 0 || minEdge < 0) {
                insets = (float) Math.ceil(mStrokeWidth / 2.0f);
            } else {
                insets = (float) (minEdge / 2.0f - mRingCenterRadius);
            }
            mStrokeInset = insets;
        }

        @SuppressWarnings("unused")
        public float getInsets() {
            return mStrokeInset;
        }

        public void setCenterRadius(double centerRadius) {
            mRingCenterRadius = centerRadius;
        }

        public double getCenterRadius() {
            return mRingCenterRadius;
        }

        public void setShowArrow(boolean show) {
            if (mShowArrow != show) {
                mShowArrow = show;
                invalidateSelf();
            }
        }

        public void setArrowScale(float scale) {
            if (scale != mArrowScale) {
                mArrowScale = scale;
                invalidateSelf();
            }
        }

        public float getStartingRotation() {
            return mStartingRotation;
        }

        public void storeOriginals() {
            mStartingStartTrim = mStartTrim;
            mStartingEndTrim = mEndTrim;
            mStartingRotation = mRotation;
        }

        public void resetOriginals() {
            mStartingStartTrim = 0;
            mStartingEndTrim = 0;
            mStartingRotation = 0;
            setStartTrim(0);
            setEndTrim(0);
            setRotation(0);
        }

        private void invalidateSelf() {
            mCallback.invalidateDrawable(null);
        }
    }
}

{% endhighlight %}

Then LoadingIndicator.

{% highlight java %}

public class LoadingIndicator extends RelativeLayout {

    public static final int DEFAULT_COLOR0 = 0xff377cc0;
    public static final int DEFAULT_COLOR1 = 0xff4eb84c;
    public static final int DEFAULT_COLOR2 = 0xffdd282f;

    protected int mOriginalOffsetTop;
    protected int mFrom;

    private CircleImageView mCircleView;
    private MaterialProgressDrawable mProgress;
    private static final int CIRCLE_BG_LIGHT = 0xFFFAFAFA;
    private static final int DEFAULT_CIRCLE_TARGET = 64;
    private static final int CIRCLE_DIAMETER_Big = 45;
    private static final float DECELERATE_INTERPOLATION_FACTOR = 2f;

    private int mCircleWidth;
    private int mCircleHeight;
    private int mCurrentTargetOffsetTop;
    private float mTotalDragDistance = -1;
    private final float REFRESH_SCALE = 1.20F;
    private int mMediumAnimationDuration;
    private Animation mScaleAnimation;
    private Animation mScaleDownAnimation;
    private DecelerateInterpolator mDecelerateInterpolator;
    private boolean mRefresh = false;

    @ColorInt
    private int color0 = DEFAULT_COLOR0;

    @ColorInt
    private int color1 = DEFAULT_COLOR1;

    @ColorInt
    private int color2 = DEFAULT_COLOR2;

    public LoadingIndicator(Context context) {
        super(context);
        initView(getContext(), null);
    }

    public LoadingIndicator(Context context, AttributeSet attrs) {
        super(context, attrs);
        initView(getContext(), attrs);
    }

    public LoadingIndicator(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        initView(getContext(), attrs);
    }

    @TargetApi(Build.VERSION_CODES.LOLLIPOP)
    public LoadingIndicator(Context context, AttributeSet attrs, int defStyleAttr, int defStyleRes) {
        super(context, attrs, defStyleAttr, defStyleRes);
        initView(getContext(), attrs);
    }

    private void initView(Context context, AttributeSet attrs) {
        TypedArray a = context.getTheme().obtainStyledAttributes(
                attrs,
                R.styleable.LoadingIndicator,
                0, 0);

        try {
            color0 = a.getColor(R.styleable.LoadingIndicator_color0, DEFAULT_COLOR0);
            color1 = a.getColor(R.styleable.LoadingIndicator_color1, DEFAULT_COLOR1);
            color2 = a.getColor(R.styleable.LoadingIndicator_color2, DEFAULT_COLOR2);
        } finally {
            a.recycle();
        }

        createProgressView();
        final DisplayMetrics metrics = getResources().getDisplayMetrics();
        mCircleHeight = mCircleWidth = (int) (CIRCLE_DIAMETER_Big * metrics.density);
        mTotalDragDistance = DEFAULT_CIRCLE_TARGET * metrics.density;
        mMediumAnimationDuration = getResources().getInteger(
                android.R.integer.config_mediumAnimTime);
        mDecelerateInterpolator = new DecelerateInterpolator(DECELERATE_INTERPOLATION_FACTOR);

        setVisibility(VISIBLE);
    }

    private void createProgressView() {
        mCircleView = new CircleImageView(getContext(), CIRCLE_BG_LIGHT);
        mProgress = new MaterialProgressDrawable(getContext(), this);
        mProgress.setBackgroundColor(CIRCLE_BG_LIGHT);
        mCircleView.setImageDrawable(mProgress);
        mCircleView.setVisibility(View.VISIBLE);
        mProgress.setAlpha(255);
        mProgress.setColorSchemeColors(color0, color1, color2);
        addView(mCircleView);
    }

    public void setScale(float scale) {
        mProgress.showArrow(true);
        float targetScale = scale;
        mProgress.setArrowScale(Math.min(1.0f, targetScale));
        mProgress.setProgressRotation((targetScale));
        mProgress.setStartEndTrim(0, Math.min(.8f, 0.8f * targetScale));
    }

    public void onRefresh(float scale) {
        mRefresh = true;
        startScaleUpAnimation(null);
        animateOffsetToCorrectPosition(mCurrentTargetOffsetTop, mRefreshListener);
    }

    public void stopRefresh() {
        mRefresh = false;
        startScaleDownAnimation(mRefreshListener);
    }

    public void startAnimation() {
        mProgress.start();
    }

    public void stopAnimation() {
        mProgress.stop();
    }

    private Animation.AnimationListener mRefreshListener = new Animation.AnimationListener() {
        @Override
        public void onAnimationStart(Animation animation) {
        }

        @Override
        public void onAnimationRepeat(Animation animation) {
        }

        @Override
        public void onAnimationEnd(Animation animation) {
            if (mRefresh) {

                mProgress.start();

            } else {
                mProgress.stop();
                mCircleView.setVisibility(View.GONE);
                ViewCompat.setScaleX(mCircleView, 0);
                ViewCompat.setScaleY(mCircleView, 0);
            }
            mCurrentTargetOffsetTop = mCircleView.getTop();
        }
    };

    private void startScaleUpAnimation(Animation.AnimationListener listener) {
        mCircleView.setVisibility(View.VISIBLE);
        mScaleAnimation = new Animation() {
            @Override
            public void applyTransformation(float interpolatedTime, Transformation t) {
                setAnimationProgress(interpolatedTime);
            }
        };
        if (listener != null) {
            mScaleAnimation.setAnimationListener(listener);
        }
        mScaleAnimation.setDuration(mMediumAnimationDuration);
        mCircleView.clearAnimation();
        mCircleView.startAnimation(mScaleAnimation);
    }

    private void startScaleDownAnimation(Animation.AnimationListener listener) {
        mScaleDownAnimation = new Animation() {
            @Override
            public void applyTransformation(float interpolatedTime, Transformation t) {
                setAnimationProgress(1 - interpolatedTime);
            }
        };
        mScaleDownAnimation.setDuration(150);
        mCircleView.setAnimationListener(listener);
        mCircleView.clearAnimation();
        mCircleView.startAnimation(mScaleDownAnimation);
    }

    private void animateOffsetToCorrectPosition(int from, Animation.AnimationListener listener) {
        mFrom = from;
        mAnimateToCorrectPosition.reset();
        mAnimateToCorrectPosition.setDuration(200);
        mAnimateToCorrectPosition.setInterpolator(mDecelerateInterpolator);
        if (listener != null) {
            mAnimateToCorrectPosition.setAnimationListener(listener);
        }
        mCircleView.clearAnimation();
        mCircleView.startAnimation(mAnimateToCorrectPosition);
    }

    @Override
    public void setVisibility(int visibility) {
        if (visibility == GONE || visibility == INVISIBLE) {

            mProgress.stop();
        } else {
            mProgress.start();
            mProgress.showArrow(true);
        }
        super.setVisibility(visibility);
    }

    private final Animation mAnimateToCorrectPosition = new Animation() {
        @Override
        public void applyTransformation(float interpolatedTime, Transformation t) {
            int targetTop = 0;
            int endTarget = 0;
            endTarget = (int) (mOriginalOffsetTop + mTotalDragDistance);
            targetTop = (mFrom + (int) ((endTarget - mFrom) * interpolatedTime));
            int offset = targetTop - mCircleView.getTop();
            setTargetOffsetTopAndBottom(offset);
        }
    };

    private void setAnimationProgress(float progress) {
        ViewCompat.setScaleX(mCircleView, progress);
        ViewCompat.setScaleY(mCircleView, progress);
    }

    private void setTargetOffsetTopAndBottom(int offset) {
        mCircleView.bringToFront();
        mCircleView.offsetTopAndBottom(offset);
        mCurrentTargetOffsetTop = mCircleView.getTop();
        invalidate();
    }

    @Override
    protected void onLayout(boolean changed, int l, int t, int r, int b) {
        super.onLayout(changed, l, t, r, b);
        final int width = getMeasuredWidth();
        int circleWidth = mCircleView.getMeasuredWidth();
        int circleHeight = mCircleView.getMeasuredHeight();
        mCircleView.layout((width / 2 - circleWidth / 2), 0,
                (width / 2 + circleWidth / 2), circleHeight);
    }

    @Override
    protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
        super.onMeasure(widthMeasureSpec, heightMeasureSpec);
        mCircleView.measure(MeasureSpec.makeMeasureSpec(mCircleWidth, MeasureSpec.EXACTLY),
                MeasureSpec.makeMeasureSpec(mCircleHeight, MeasureSpec.EXACTLY));

    }
}

{% endhighlight %}

Last step, add res/values/attrs.xml

{% highlight xml %}

<?xml version="1.0" encoding="utf-8"?>
<resources>
    <declare-styleable name="LoadingIndicator">
        <attr name="color0" format="color" />
        <attr name="color1" format="color" />
        <attr name="color2" format="color" />
    </declare-styleable>
</resources>

{% endhighlight %}

and layout/view_progress_bar.xml

{% highlight xml %}

<?xml version="1.0" encoding="utf-8"?>
<android.support.constraint.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:id="@+id/progress_layout"
    android:clickable="true">

    <com.example.base.views.loading_indicator.LoadingIndicator
        android:layout_width="64dp"
        android:layout_height="64dp"
        android:layout_gravity="center"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintVertical_bias="0.5"
        app:color0="@color/blue"
        app:color1="@color/blue"
        app:color2="@color/blue"/>
</android.support.constraint.ConstraintLayout>

{% endhighlight %}

Every thing done, Add util method which add loading indicator to your Activity/Fragment.

{% highlight java %}

public static void showOrHideProgressView(Activity activity, boolean showOrHide) {
        showOrHideProgressView(activity, activity.findViewById(android.R.id.content), showOrHide);
    }

public static void showOrHideProgressView(Context context, ViewGroup viewGroup, boolean showOrHide) {
    View view = viewGroup.findViewById(R.id.progress_layout);
    if (showOrHide) {
        if (view == null) {
            View progressView = LayoutInflater.from(context).inflate(R.layout.view_progress_bar, viewGroup, false);
            viewGroup.addView(progressView);
        }
    } else {
        if (view != null) {
            viewGroup.removeView(view);
        }
    }
}

public static boolean isShowingProgress(Activity activity) {
    ViewGroup viewGroup = activity.findViewById(android.R.id.content);
    View view = viewGroup.findViewById(R.id.progress_layout);
    return view != null;
}

{% endhighlight %}