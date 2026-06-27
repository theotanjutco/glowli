import { View, Text, TouchableOpacity } from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';

type Props = {
  navigation: NativeStackNavigationProp<any>;
};

export default function CameraScreen({ navigation }: Props) {
  return (
    <View className="flex-1 items-center justify-center bg-gray-900">
      <Text className="text-white text-2xl font-bold mb-4">
        Camera Screen
      </Text>
      <Text className="text-gray-400 mb-8">
        Camera will go here in Phase 4
      </Text>
      <TouchableOpacity
        className="bg-pink-500 px-8 py-4 rounded-full"
        onPress={() => navigation.goBack()}
      >
        <Text className="text-white font-bold">
          Go Back
        </Text>
      </TouchableOpacity>
    </View>
  );
}