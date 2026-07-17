import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

import LoginScreen from "./src/screens/LoginScreen";
import CaptureScreen from "./src/screens/CaptureScreen";

const Stack = createNativeStackNavigator();
console.log("Login Screen Loaded");
export default function App() {
  return (
    <NavigationContainer>

      <Stack.Navigator
        initialRouteName="Login"
        screenOptions={{
          headerShown: false,
        }}
      >

        <Stack.Screen
          name="Login"
          component={LoginScreen}
        />

        <Stack.Screen
          name="Capture"
          component={CaptureScreen}
        />

      </Stack.Navigator>

    </NavigationContainer>
  );
}