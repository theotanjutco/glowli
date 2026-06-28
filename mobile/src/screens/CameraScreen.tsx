import { View, Text, TouchableOpacity } from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';

type Props = {
  navigation: NativeStackNavigationProp<any>;
};

export default function CameraScreen({ navigation }: Props) {
  return (
    <View className="flex-1 items-center justify-center bg-gray-900">
      <Text className="mb-4 text-2xl font-bold text-white">
        Camera Screen
      </Text>
      <Text className="mb-8 text-gray-400">
        Camera will go here in Phase 4
      </Text>
      <TouchableOpacity
        className="rounded-full bg-pink-500 px-8 py-4"
        onPress={() => navigation.goBack()}
      >
        <Text className="font-bold text-white">
          Go Back
        </Text>
      </TouchableOpacity>
    </View>
  );
}