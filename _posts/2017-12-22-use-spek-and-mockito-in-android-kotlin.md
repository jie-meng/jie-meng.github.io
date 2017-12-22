---
title: Use Spek and Mockito in Android Kotlin
layout: post
date: '2017-12-22 15:39:00 +0800'
categories: android
---

Create an Android kotlin project.

Add dependencies to app/build.gradle

{% highlight groovy %}
testImplementation 'org.mockito:mockito-core:2.+'
testImplementation 'org.jetbrains.spek:spek-api:1.1.2'
testImplementation 'org.jetbrains.spek:spek-junit-platform-engine:1.1.2'
testImplementation 'org.junit.platform:junit-platform-runner:1.0.0-M4'
testImplementation 'org.junit.jupiter:junit-jupiter-api:5.0.0-M4'
{% endhighlight %}

Implement an interface `DataSource`.
{% highlight kotlin %}
interface DataSource {
    fun fetch(inputA: Int, inputB: Arg): Int
}
{% endhighlight %}

Implement a class `Arg`.
{% highlight kotlin %}
class Arg(name: String) {
    val name = name.toUpperCase()
}
{% endhighlight %}

Replace content of test file `ExampleUnitTest.kt` to
{% highlight kotlin %}
@RunWith(JUnitPlatform::class)
class MomentsPresenterSpec : Spek({

    val dataSource = Mockito.mock(DataSource::class.java)

    beforeEachTest {
    }

    afterEachTest {
    }

    describe("DataSource fetch") {

        given("with any input data") {
            beforeEachTest {
                Mockito.`when`(dataSource.fetch(anyInt(), any(Arg::class.java))).thenReturn(1)
            }

            it("should return 1") {
                assertEquals(1, dataSource.fetch(0, Arg("Jie")))
            }
        }
    }
})
{% endhighlight %}

Run test, then you would got:
`java.lang.IllegalStateException: any(Arg::class.java) must not be null`

That's because any() always return default value of given class, for primitive type, it'll return primitive default value, for class, null will return.

Kotlin method does not accept null value if not declared nullable as `arg: ClassName?`.

You can override any() function to solve this problem.

Add a utils file `Extensions.kt` to test project.

{% highlight kotlin %}
fun <T> any(): T {
    Mockito.any<T>()
    return uninitialized()
}

fun <T> uninitialized(): T = null as T
{% endhighlight %}

Make some change to `ExampleUnitTest.kt`

From 

```Mockito.`when`(dataSource.fetch(anyInt(), any(Arg::class.java))).thenReturn(1)```

to 

```Mockito.`when`(dataSource.fetch(anyInt(), any())).thenReturn(1)```

Add import `import com.jmengxy.kotlinspek.utils.any`

Re-Run test, everything works fine.

[Github Repo](https://github.com/jie-meng/KotlinSpek)

## References

[Using spek in kotlin](https://stackoverflow.com/questions/44919436/java-lang-classnotfoundexception-com-intellij-junit5-junit5ideatestrunner-using)

[Befriending Kotlin and Mockito](https://medium.com/@elye.project/befriending-kotlin-and-mockito-1c2e7b0ef791)