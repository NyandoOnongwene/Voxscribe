# VoxScribe Model Evaluation Report

Generated on: 2025-06-27 00:44:31

## Evaluation Results

### translation_metrics_en_fr_20250627_004431

- **bleu_score**: 0.4000
- **f1_score**: 0.7294
- **accuracy**: 0.4000
- **character_error_rate**: 0.2542
- **character_accuracy**: 0.7458
- **semantic_similarity**: 0.6463
- **avg_reference_length**: 5.0000
- **avg_prediction_length**: 5.2667
- **length_ratio**: 1.0533
- **avg_processing_time**: 2.1436
- **total_translations**: 15
- **successful_translations**: 15
- **source_language**: en
- **target_language**: fr

### translation_metrics_en_fr_20250627_003800

- **bleu_score**: 0.4667
- **f1_score**: 0.7961
- **accuracy**: 0.4667
- **character_error_rate**: 0.2057
- **character_accuracy**: 0.7943
- **semantic_similarity**: 0.7129
- **avg_reference_length**: 5.0000
- **avg_prediction_length**: 5.2000
- **length_ratio**: 1.0400
- **avg_processing_time**: 2.2847
- **total_translations**: 15
- **successful_translations**: 15
- **source_language**: en
- **target_language**: fr

### stt_metrics_20250627_004359

- **word_error_rate**: 0.1602
- **character_error_rate**: 0.1286
- **f1_score**: 0.9164
- **accuracy**: 0.4000
- **bleu_score**: 0.4274
- **word_accuracy**: 0.6554
- **avg_processing_time**: 0.0002
- **avg_confidence_score**: 0.8960
- **total_texts**: 15
- **successful_transcriptions**: 15

### stt_metrics_20250627_003726

- **word_error_rate**: 0.1568
- **character_error_rate**: 0.1019
- **f1_score**: 0.9116
- **accuracy**: 0.3333
- **bleu_score**: 0.4598
- **word_accuracy**: 0.6698
- **avg_processing_time**: 0.0004
- **avg_confidence_score**: 0.9038
- **total_texts**: 15
- **successful_transcriptions**: 15

## Metric Interpretations

### Speech-to-Text Metrics
- **Word Error Rate (WER)**: Lower is better (0 = perfect)
- **Character Error Rate (CER)**: Lower is better (0 = perfect)
- **Accuracy**: Higher is better (1 = perfect)
- **F1 Score**: Higher is better (1 = perfect)
- **BLEU Score**: Higher is better (1 = perfect)
- **Word Accuracy**: Higher is better (1 = perfect)

### Translation Metrics
- **BLEU Score**: Higher is better (1 = perfect)
- **F1 Score**: Higher is better (1 = perfect)
- **Accuracy**: Higher is better (1 = perfect)
- **Character Accuracy**: Higher is better (1 = perfect)
- **Semantic Similarity**: Higher is better (1 = perfect)

## Performance Benchmarks

### Expected Performance Ranges
- **Good STT Performance**: WER < 0.15, F1 > 0.85
- **Good Translation Performance**: BLEU > 0.4, F1 > 0.6
- **Excellent Performance**: All metrics in top 10% of benchmark

