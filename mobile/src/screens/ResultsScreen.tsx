import { View, Text, TouchableOpacity } from 'react-native';

type Props = {
    route: any;
};

// Shows the mock analysis returned by FastAPI.
export default function ResultsScreen({ route }: Props) {
    const { analysis } = route.params; 

    return (
        <View>
            <Text>Your Glowli Scan</Text>
            <Text>{analysis.summary}</Text>
            <Text>Skin Type: {analysis.skin_type}</Text>

            {analysis.conditions.map((condition: any) => (
                <View key={condition.label}>
                    <Text>{condition.label}</Text>
                    <Text>Severity: {condition.severity}</Text>
                    <Text>Confidence: {Math.round(condition.confidence * 100)}%</Text>
                    <Text>{condition.description}</Text>
                </View>
            ))}
        </View>
    );
}