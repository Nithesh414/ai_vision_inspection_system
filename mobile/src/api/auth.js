import api from "./client";
import AsyncStorage from "@react-native-async-storage/async-storage";

export async function login(username, password) {

    console.log("Connecting to:", api.defaults.baseURL);

    const body = new URLSearchParams();

    body.append("username", username);
    body.append("password", password);

    const response = await api.post(
        "/api/auth/login",
        body.toString(),
        {
            headers:{
                "Content-Type":"application/x-www-form-urlencoded"
            }
        }
    );

    console.log(response.data);

    await AsyncStorage.setItem(
        "access_token",
        response.data.access_token
    );

    return response.data;
}