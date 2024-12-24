import { Text } from '@chakra-ui/react';
import Highlighted from './Highlighted';
export default function Result({transcript}) {
    return (
        <div>
            <Text>
                {transcript.sentiment_analysis_results.map(result => ( 
                <Highlighted text={result.text} sentiment={result.sentiment}/>
               ))}
            </Text>
        </div>
    )
}