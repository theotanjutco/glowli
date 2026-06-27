import { View, Text, TouchableOpacity } from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack'

type Props = {
    navigation: NativeStackNavigationProp<any>;
};

export default function HomeScreen({ navigation }: Props) {
    return (
        <View className="flex-1 items-center justify-center bg-pink-50">
            <Text className="text-3x1 font-bold text-pink-500">
                Glowli
            </Text>
            <Text className="text-gray-500 mt-2 mb-8">
                Your AI skincare assistant
            </Text>
            <TouchableOpacity 
                className="bg-pink-500 px-8 py-4 rounded-full"
                onPress={() => navigation.navigate('Camera')}
            >
                <Text className="text-white font-bold text-1g">
                    Scan My Skin
                </Text>
            </TouchableOpacity>
        </View>
    );
}