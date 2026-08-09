import { View, Text, TouchableOpacity, ActivityIndicator, Alert, Image } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useState } from 'react';
import { analyzeSelfie, getAPIErrorMessage } from '../api/glowli';
import type  { RootStackParamList } from '../types/navigation';
import * as ImagePicker from 'expo-image-picker';
// expo-image-picker may not have type declarations in this project setup.
// Use require and type it as any to avoid TS module/type errors.
// eslint-disable-next-line @typescript-eslint/no-var-requires
//const ImagePicker: any = require('expo-image-picker');

type Props = NativeStackScreenProps<RootStackParamList, 'Camera'>;

export default function CameraScreen({ navigation }: Props) {

  // Storing the selected image URI
  const [selectedImageUri, setSelectedImageUri] = useState<string | null>(null);

  // Track analysis request
  const [isAnalyzing, setisAnalyzing] = useState(false);

  // Opening photo library and sending image to FastAPI
  async function chooseandAnalyzeSelfie() : Promise<void> {

    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (!permission || !permission.granted) {
      Alert.alert(
        'Photo access required',
        'Glowli needs photo access so you can choose a selfie.');
      return;
    }
    
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.85,
    });

    if (result.canceled) {
      return;
    }

    const selectedURI = result.assets[0]?.uri

    if (!selectedURI) {
      Alert.alert('Image Unavailable', 'Glowli could not access the selected image');
      return;
    }

    setSelectedImageUri(selectedURI);
    setisAnalyzing(true);

    // Attempt the call that can fail because of networking or backend validation.
    try {
      // Uploaded the selfie to FastAPI and get the analysis
      const analysis = await analyzeSelfie(selectedURI);

      setisAnalyzing(false);

      navigation.navigate('Results', { analysis }); 

    } catch (error) {

      setisAnalyzing(false);

      Alert.alert('Scan failed', getAPIErrorMessage(error));
    }
  }
  return (
    <View className="flex-1 items-center justify-center bg-gray-900">
      <Text className="mb-4 text-2xl font-bold text-white">
        Camera Screen
      </Text>
      { selectedImageUri ? (
        <Image
          source = {{ uri: selectedImageUri }}
          className = "mb-6 h-64 w-63 rounded-3Xl"
        />
      ) : (
        <Text className = "mb-6 text-center text-gray-400">
          Select a clear, well-lit selfie to test out Glowli's skin analysis.
        </Text>
      )}

      { isAnalyzing ? (
        <View className = "mb-8 items-center">
          <ActivityIndicator size="large" color="#ec4899" />

          <Text className = "mb-4 text-white">
            Analyzing your selfie...
          </Text>
        </View>
      ) : null}

      <TouchableOpacity
        className={`rounded-full bg-pink-500 px-8 py-4 ${
          isAnalyzing ? 'opacity-50' : 'opacity-100'
        }`}

        onPress={chooseandAnalyzeSelfie}
        disabled={isAnalyzing}
      ></TouchableOpacity>

      <TouchableOpacity
        className="mt-6 px-6 py-3"
        onPress={() => navigation.goBack()}
        disabled={isAnalyzing}
      >
        <Text className="font-semibold text-gray-300">
        Go Back to Home Screen
        </Text>
      </TouchableOpacity>
    </View>
  );
}