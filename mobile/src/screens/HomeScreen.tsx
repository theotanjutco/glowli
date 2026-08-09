import { View, Text, TouchableOpacity } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack'

// Import only Glowli's route definitions.
import type { RootStackParamList } from '../types/navigation';

type Props = NativeStackScreenProps<RootStackParamList, 'Home'>;

export default function HomeScreen({ navigation }: Props) {
    return (
        <View className="flex-1 items-center justify-center bg-pink-50">
            <Text className="text-3xl font-bold text-pink-500">
                Glowli
            </Text>
            <Text className="mt-2 mb-8 text-gray-500">
                Your AI skincare assistant
            </Text>
            <TouchableOpacity
                className="rounded-full bg-pink-500 px-8 py-4"
                onPress={() => navigation.navigate('Camera')}
            >
                <Text className="text-lg font-bold text-white">
                    Scan My Skin
                </Text>
            </TouchableOpacity>
        </View>
    );
}