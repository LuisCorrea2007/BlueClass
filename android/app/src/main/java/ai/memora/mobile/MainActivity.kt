package ai.memora.mobile

import android.app.Activity
import android.os.Bundle
import android.content.Intent
import android.graphics.Color
import android.view.Gravity
import android.widget.*
import org.json.JSONArray
import org.json.JSONObject

class MainActivity : Activity() {
    private val prefs by lazy { getSharedPreferences("memora", MODE_PRIVATE) }
    private lateinit var titleField: EditText
    private lateinit var contentField: EditText
    private lateinit var list: LinearLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(24, 36, 24, 24)
            setBackgroundColor(Color.rgb(12, 18, 30))
        }
        fun label(s: String, size: Float = 15f) = TextView(this).apply {
            text = s; textSize = size; setTextColor(Color.WHITE); setPadding(0, 12, 0, 12)
        }
        titleField = EditText(this).apply { hint = "Memory title"; setTextColor(Color.WHITE); setHintTextColor(0xffaab4c5.toInt()) }
        contentField = EditText(this).apply { hint = "Paste or share a conversation"; minLines = 5; gravity = Gravity.TOP; setTextColor(Color.WHITE); setHintTextColor(0xffaab4c5.toInt()) }
        root.addView(label("MEMORA AI", 26f))
        root.addView(label("Your portable memory layer"))
        root.addView(titleField)
        root.addView(contentField)
        root.addView(Button(this).apply { text = "Save memory"; setOnClickListener { saveMemory() } })
        root.addView(label("Saved on this device"))
        list = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        root.addView(list)
        val scroll = ScrollView(this).apply { addView(root) }
        setContentView(scroll)
        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            contentField.setText(intent.getStringExtra(Intent.EXTRA_TEXT).orEmpty())
            titleField.setText(intent.getStringExtra(Intent.EXTRA_SUBJECT) ?: "Shared conversation")
        }
        render()
    }

    private fun records(): JSONArray = try { JSONArray(prefs.getString("memories", "[]")) } catch (_: Exception) { JSONArray() }

    private fun saveMemory() {
        val body = contentField.text.toString().trim()
        if (body.isBlank()) { Toast.makeText(this, "Add content first", Toast.LENGTH_SHORT).show(); return }
        val item = JSONObject()
            .put("id", java.util.UUID.randomUUID().toString())
            .put("title", titleField.text.toString().ifBlank { "Untitled memory" })
            .put("content", body)
            .put("created_at", System.currentTimeMillis())
        val all = records(); all.put(item)
        prefs.edit().putString("memories", all.toString()).apply()
        titleField.text.clear(); contentField.text.clear()
        render()
        Toast.makeText(this, "Memory saved locally", Toast.LENGTH_SHORT).show()
    }

    private fun render() {
        list.removeAllViews()
        val all = records()
        for (i in all.length() - 1 downTo 0) {
            val item = all.optJSONObject(i) ?: continue
            list.addView(TextView(this).apply {
                text = item.optString("title") + "\n" + item.optString("content")
                textSize = 14f; setTextColor(Color.WHITE); setPadding(16, 16, 16, 16)
                setBackgroundColor(Color.rgb(29, 40, 58))
            })
        }
        if (all.length() == 0) list.addView(TextView(this).apply { text = "No memories yet."; setTextColor(Color.LTGRAY) })
    }
}