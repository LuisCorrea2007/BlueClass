package ai.memora.mobile
import android.app.Activity
import android.os.Bundle
import android.content.Intent
import android.graphics.Color
import android.view.Gravity
import android.text.InputType
import android.widget.*
import org.json.JSONArray
import org.json.JSONObject
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

class MainActivity : Activity() {
 private val prefs by lazy {
  val key=MasterKey.Builder(this).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build()
  EncryptedSharedPreferences.create(this,"memora_secure",key,
   EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
   EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM)
 }
 private lateinit var title:EditText
 private lateinit var body:EditText
 private lateinit var server:EditText
 private lateinit var token:EditText
 private lateinit var status:TextView
 private lateinit var records:LinearLayout
 private val panel=Color.rgb(18,27,41)
 override fun onCreate(savedInstanceState:Bundle?){super.onCreate(savedInstanceState);ui();accept(intent);render()}
 override fun onNewIntent(i:Intent){super.onNewIntent(i);setIntent(i);accept(i)}
 private fun ui(){
  val root=LinearLayout(this).apply{orientation=1;setPadding(24,32,24,24);setBackgroundColor(Color.rgb(11,15,22))}
  fun label(s:String)=TextView(this).apply{text=s;textSize=14f;setTextColor(-1);setPadding(0,10,0,10)}
  fun field(h:String,m:Boolean=false)=EditText(this).apply{hint=h;setTextColor(-1);setHintTextColor(0xff8995a8.toInt());setBackgroundColor(panel);if(m){minLines=5;gravity=Gravity.TOP}}
  root.addView(label("✳ MEMORA AI"))
  root.addView(label("Your knowledge, portable"))
  server=field("HTTPS API URL");server.setText(prefs.getString("api_url",""));root.addView(server)
  token=field("Bearer token (if enabled)").apply{inputType=InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD};token.setText(prefs.getString("api_token",""));root.addView(token)
  root.addView(Button(this).apply{text="Save connection";setOnClickListener{prefs.edit().putString("api_url",server.text.toString().trim().trimEnd('/')).putString("api_token",token.text.toString().trim()).apply();status.text="Connection saved."}})
  title=field("Memory title");body=field("Text to remember",true);root.addView(title);root.addView(body)
  val actions=LinearLayout(this).apply{orientation=0}
  actions.addView(Button(this).apply{text="Save locally";setOnClickListener{save()}},LinearLayout.LayoutParams(0,-2,1f))
  actions.addView(Button(this).apply{text="Sync now";setOnClickListener{sync()}},LinearLayout.LayoutParams(0,-2,1f));root.addView(actions)
  status=label("Encrypted local storage");root.addView(status);root.addView(label("Recent memories"))
  records=LinearLayout(this).apply{orientation=1};root.addView(records)
  setContentView(ScrollView(this).apply{addView(root)})
 }
 private fun accept(i:Intent?){if(i?.action==Intent.ACTION_SEND&&i.type=="text/plain"){body.setText(i.getCharSequenceExtra(Intent.EXTRA_TEXT)?.toString().orEmpty());title.setText(i.getStringExtra(Intent.EXTRA_SUBJECT)?:"Shared conversation")}}
 private fun all()=try{JSONArray(prefs.getString("memories","[]"))}catch(_:Exception){JSONArray()}
 private fun saveAll(a:JSONArray){prefs.edit().putString("memories",a.toString()).apply()}
 private fun save(){
  val text=body.text.toString().trim();if(text.isBlank()){status.text="Enter content first.";return}
  val a=all();a.put(JSONObject().put("id",java.util.UUID.randomUUID().toString()).put("title",title.text.toString().ifBlank{"Untitled"}).put("content",text).put("source","android").put("tags",JSONArray(listOf("mobile"))).put("synced",false))
  saveAll(a);body.text.clear();title.text.clear();status.text="Saved securely on this device.";render()
 }
 private fun sync(){
  val base=prefs.getString("api_url","").orEmpty().trimEnd('/');if(!base.startsWith("https://")){status.text="Set an HTTPS API URL first.";return}
  val bearer=prefs.getString("api_token","").orEmpty();status.text="Synchronizing…"
  thread { try {
   val a=all();var uploaded=0
   for(n in 0 until a.length()){val x=a.optJSONObject(n)?:continue;if(x.optBoolean("synced"))continue
    val p=JSONObject().put("title",x.optString("title")).put("content",x.optString("content")).put("source","android").put("source_ref",x.optString("id")).put("tags",x.optJSONArray("tags")?:JSONArray())
    val c=URL("$base/api/memories").openConnection() as HttpURLConnection;c.requestMethod="POST";c.connectTimeout=12000;c.readTimeout=12000;c.doOutput=true;c.setRequestProperty("Content-Type","application/json");if(bearer.isNotBlank())c.setRequestProperty("Authorization","Bearer $bearer")
    c.outputStream.use{it.write(p.toString().toByteArray())};if(c.responseCode !in 200..299)error("Upload HTTP ${c.responseCode}")
    val result=JSONObject(c.inputStream.bufferedReader().use{it.readText()});x.put("cloud_id",result.optString("id")).put("synced",true);uploaded++;saveAll(a);c.disconnect()
   }
   val c=URL("$base/api/memories?limit=500").openConnection() as HttpURLConnection;c.connectTimeout=12000;c.readTimeout=12000;if(bearer.isNotBlank())c.setRequestProperty("Authorization","Bearer $bearer");if(c.responseCode !in 200..299)error("Download HTTP ${c.responseCode}")
   val cloud=JSONArray(c.inputStream.bufferedReader().use{it.readText()});c.disconnect();val known=HashSet<String>();for(n in 0 until a.length())known.add(a.optJSONObject(n)?.optString("cloud_id").orEmpty());var downloaded=0
   for(n in 0 until cloud.length()){val x=cloud.optJSONObject(n)?:continue;val id=x.optString("id");if(id.isNotBlank()&&!known.contains(id)){a.put(JSONObject().put("id",java.util.UUID.randomUUID().toString()).put("cloud_id",id).put("title",x.optString("title")).put("content",x.optString("content")).put("synced",true));known.add(id);downloaded++}}
   saveAll(a);runOnUiThread{status.text="Sync complete: $uploaded uploaded, $downloaded downloaded.";render()}
  }catch(e:Exception){runOnUiThread{status.text="Sync failed: ${e.message}. Local data retained."}} }
 }
 private fun render(){records.removeAllViews();val a=all();for(n in a.length()-1 downTo 0){val x=a.optJSONObject(n)?:continue;records.addView(TextView(this).apply{text=x.optString("title")+"\n"+x.optString("content")+"\n"+if(x.optBoolean("synced"))"CLOUD SYNCED" else "LOCAL · PENDING";setTextColor(-1);setPadding(14,14,14,14);setBackgroundColor(panel)})}}
}