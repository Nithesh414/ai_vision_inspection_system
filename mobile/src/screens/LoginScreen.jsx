import React, { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from "react-native";
import { login } from "../api/client";

export default function LoginScreen({ navigation }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

async function handleLogin() {
  console.log("Login button pressed");

  setLoading(true);

  try {
    console.log("Username:", username);

    const data = await login(username, password);

    console.log("Login Success");
    console.log(data);

    navigation.replace("Capture");
  } catch (err) {
    console.log("========== LOGIN ERROR ==========");
    console.log(err);
    console.log(err.response);
    console.log(err.message);

    Alert.alert(
      "Login failed",
      err.response?.data?.detail || err.message
    );
  } finally {
    setLoading(false);
  }
}

  return (
    <View style={styles.container}>
      <Text style={styles.eyebrow}>QC STATION ACCESS</Text>
      <Text style={styles.title}>Sign in to inspect</Text>

      <TextInput style={styles.input} placeholder="Username" value={username} onChangeText={setUsername} autoCapitalize="none" />
      <TextInput style={styles.input} placeholder="Password" value={password} onChangeText={setPassword} secureTextEntry />

      <TouchableOpacity style={styles.button} onPress={handleLogin} disabled={loading}>
        <Text style={styles.buttonText}>{loading ? "Signing in…" : "Sign in"}</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", padding: 24, backgroundColor: "#14181d" },
  eyebrow: { color: "#f0a202", fontSize: 12, letterSpacing: 1.5, marginBottom: 6 },
  title: { color: "#fff", fontSize: 24, fontWeight: "700", marginBottom: 24 },
  input: { backgroundColor: "#fff", borderRadius: 8, padding: 14, marginBottom: 12, fontSize: 15 },
  button: { backgroundColor: "#f0a202", borderRadius: 8, padding: 14, alignItems: "center", marginTop: 8 },
  buttonText: { fontWeight: "700", color: "#201703" },
});
