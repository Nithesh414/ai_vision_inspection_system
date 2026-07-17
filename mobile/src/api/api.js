import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { API_BASE_URL } from "./config";

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
});

api.interceptors.request.use(async (config) => {

    const token = await AsyncStorage.getItem("access_token");

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    console.log("==================================");
    console.log("REQUEST");
    console.log(config.baseURL + config.url);
    console.log("==================================");

    return config;
});

api.interceptors.response.use(

    response => {

        console.log("SUCCESS");
        console.log(response.status);

        return response;
    },

    error => {

        console.log("REQUEST FAILED");

        if (error.response) {

            console.log(error.response.status);
            console.log(error.response.data);

        } else {

            console.log(error.message);

        }

        return Promise.reject(error);
    }

);

export default api;