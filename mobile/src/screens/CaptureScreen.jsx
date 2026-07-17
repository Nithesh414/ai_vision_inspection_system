import React, { useEffect, useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet, Image, ScrollView, ActivityIndicator, Alert } from "react-native";
import * as ImagePicker from "expo-image-picker";
import { Picker } from "@react-native-picker/picker";
import { getProducts, submitInspection } from "../api/client";

export default function CaptureScreen({ navigation }) {
  const [products, setProducts] = useState([]);
  const [productId, setProductId] = useState("");
  const [photo, setPhoto] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getProducts().then(setProducts).catch(() => Alert.alert("Error", "Could not load products."));
  }, []);

  async function takePhoto() {
    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (!perm.granted) return Alert.alert("Camera permission required");
    const res = await ImagePicker.launchCameraAsync({ quality: 0.9 });
    if (!res.canceled) {
      setPhoto(res.assets[0].uri);
      setResult(null);
    }
  }

  async function runInspection() {
    if (!productId || !photo) return Alert.alert("Select a product and capture a photo first.");
    setLoading(true);
    try {
      const data = await submitInspection(productId, photo);
      setResult(data);
    } catch (err) {
      Alert.alert("Inspection failed", err.response?.data?.detail || "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 20 }}>
      <Text style={styles.eyebrow}>OPERATOR CONSOLE</Text>
      <Text style={styles.title}>New Inspection</Text>

      <View style={styles.pickerWrap}>
        <Picker selectedValue={productId} onValueChange={setProductId}>
          <Picker.Item label="Select product…" value="" />
          {products.map((p) => <Picker.Item key={p.id} label={`${p.name} (${p.code})`} value={p.id} />)}
        </Picker>
      </View>

      <TouchableOpacity style={styles.secondaryButton} onPress={takePhoto}>
        <Text style={styles.secondaryButtonText}>Capture Product Photo</Text>
      </TouchableOpacity>

      {photo && <Image source={{ uri: photo }} style={styles.preview} />}

      <TouchableOpacity style={styles.button} onPress={runInspection} disabled={loading}>
        {loading ? <ActivityIndicator color="#201703" /> : <Text style={styles.buttonText}>Run Inspection</Text>}
      </TouchableOpacity>

      {result && (

<View style={styles.resultCard}>

<Text
style={[
styles.stamp,
result.status==="PASS"
?styles.pass
:styles.fail
]}
>

{result.status}

</Text>

<Text style={styles.meta}>
Confidence : {result.confidence.toFixed(2)}%
</Text>

<Text style={styles.meta}>
Inspection Time :
{" "}
{result.inspection_time_seconds}s
</Text>

<Text
style={{
fontWeight:"bold",
marginTop:10
}}
>

Reasons

</Text>

{result.reasons.map((r,i)=>(

<Text key={i}>
• {r}
</Text>

))}

<Text
style={{
fontWeight:"bold",
marginTop:15
}}
>

Suggested Actions

</Text>

{result.suggested_actions.map((a,i)=>(

<Text key={i}>
• {a}
</Text>

))}

</View>

)}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f6f4" },
  eyebrow: { color: "#5b6672", fontSize: 12, letterSpacing: 1.2 },
  title: { fontSize: 22, fontWeight: "700", marginBottom: 16 },
  pickerWrap: { backgroundColor: "#fff", borderRadius: 8, marginBottom: 12, borderWidth: 1, borderColor: "#d8dbd6" },
  secondaryButton: { backgroundColor: "#1b2128", borderRadius: 8, padding: 14, alignItems: "center", marginBottom: 12 },
  secondaryButtonText: { color: "#fff", fontWeight: "600" },
  preview: { width: "100%", height: 220, borderRadius: 8, marginBottom: 12 },
  button: { backgroundColor: "#f0a202", borderRadius: 8, padding: 14, alignItems: "center" },
  buttonText: { fontWeight: "700", color: "#201703" },
  resultCard: { backgroundColor: "#fff", borderRadius: 10, padding: 16, marginTop: 20 },
  stamp: { fontWeight: "800", fontSize: 16, marginBottom: 8, alignSelf: "flex-start", paddingHorizontal: 10, paddingVertical: 4, borderRadius: 4, borderWidth: 2 },
  pass: { color: "#1f9d55", borderColor: "#1f9d55", backgroundColor: "#eefaf1" },
  fail: { color: "#d13b3b", borderColor: "#d13b3b", backgroundColor: "#fdeeee" },
  meta: { color: "#5b6672", marginBottom: 10 },
  reason: { fontSize: 14, marginBottom: 4 },
});
