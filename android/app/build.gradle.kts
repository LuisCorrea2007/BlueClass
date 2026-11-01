plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}
android {
    namespace = "ai.memora.mobile"
    compileSdk = 35
    defaultConfig {
        // Separate package keeps the already-installed first build and its local memories intact.
        applicationId = "ai.memora.mobile.sync"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "0.2.0"
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
kotlin { jvmToolchain(17) }
dependencies {
    implementation("androidx.security:security-crypto:1.1.0-alpha06")
}