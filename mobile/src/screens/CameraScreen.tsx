import { View, Text, TouchableOpacity } from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
// expo-image-picker may not have type declarations in this project setup.
// Use require and type it as any to avoid TS module/type errors.
// eslint-disable-next-line @typescript-eslint/no-var-requires
const ImagePicker: any = require('expo-image-picker');

type Props = {
  navigation: NativeStackNavigationProp<any>;
};

export default function CameraScreen({ navigation }: Props) {

  // Let the User choose a selfie before sending it to /analyze endpoint
  async function chooseSelfie() {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (!permission || !permission.granted) {
      alert('Glowli needs photo access');
      return;
    }
    
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.85,
    });

    if (!result.canceled) {
      return result.assets[0].uri;
    }
  }
  return (
    <View className="flex-1 items-center justify-center bg-gray-900">
      <Text className="mb-4 text-2xl font-bold text-white">
        Camera Screen
      </Text>
      <Text className="mb-8 text-gray-400">
        <TouchableOpacity
          className="rounded-full bg-pink-500 px-8 py-4"
          onPress={chooseSelfie}
        >
          <Text className="font-bold text-white">
            Choose Selfie
          </Text>
        </TouchableOpacity>
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