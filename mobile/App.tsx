import { StatusBar } from 'expo-status-bar';
import { Text, View } from 'react-native';

export default function App() {
  return (
    <View className="flex-1 items-center justify-center bg-pink-50">
      <Text className="text-3xl font-bold text-pink-500">
        Glowli
      </Text>
      <Text className="text-gray-500 mt-2">
        Your AI skincare assistant
      </Text>
      <StatusBar style="auto" />
    </View>
  );
}

