# VoxScribe Model Evaluation Framework Documentation

## Overview

The VoxScribe Model Evaluation Framework provides comprehensive assessment of the speech-to-text and translation components using industry-standard metrics. This ensures quality assurance, performance monitoring, and transparency for the bilingual conversation system.

## 🎯 Why Model Evaluation Matters

- **Quality Assurance**: Measure system performance against established benchmarks
- **Performance Monitoring**: Track improvements or degradation over time
- **User Trust**: Provide transparency about system capabilities and limitations
- **Optimization**: Identify specific areas requiring improvement
- **Deployment Decisions**: Determine production readiness

## 📊 Evaluation Metrics

### Speech-to-Text (STT) Metrics

#### 1. Word Error Rate (WER)
- **Definition**: Percentage of words incorrectly transcribed
- **Formula**: `(Substitutions + Deletions + Insertions) / Total Reference Words`
- **Range**: 0.0 (perfect) to 1.0+ (very poor)
- **Interpretation**:
  - ✅ **Excellent**: WER < 0.05
  - ✅ **Good**: WER < 0.15
  - ⚠️ **Fair**: WER < 0.25
  - ❌ **Poor**: WER ≥ 0.25

#### 2. Character Error Rate (CER)
- **Definition**: Percentage of characters incorrectly transcribed
- **Formula**: Same as WER but at character level
- **Range**: 0.0 (perfect) to 1.0+ (very poor)
- **Interpretation**:
  - ✅ **Excellent**: CER < 0.03
  - ✅ **Good**: CER < 0.10
  - ⚠️ **Fair**: CER < 0.20
  - ❌ **Poor**: CER ≥ 0.20

#### 3. F1 Score (STT)
- **Definition**: Harmonic mean of precision and recall for word overlap
- **Formula**: `2 × (Precision × Recall) / (Precision + Recall)`
- **Range**: 0.0 (poor) to 1.0 (perfect)
- **Interpretation**:
  - ✅ **Excellent**: F1 > 0.95
  - ✅ **Good**: F1 > 0.85
  - ⚠️ **Fair**: F1 > 0.70
  - ❌ **Poor**: F1 ≤ 0.70

#### 4. BLEU Score (STT)
- **Definition**: Measures n-gram overlap between reference and transcription
- **Range**: 0.0 (no overlap) to 1.0 (perfect match)
- **Interpretation**:
  - ✅ **Excellent**: BLEU > 0.80
  - ✅ **Good**: BLEU > 0.60
  - ⚠️ **Fair**: BLEU > 0.40
  - ❌ **Poor**: BLEU ≤ 0.40

#### 5. Exact Match Accuracy
- **Definition**: Percentage of transcriptions that exactly match the reference
- **Range**: 0.0 (0%) to 1.0 (100%)
- **Note**: Strict metric, often lower than other measures

#### 6. Word Accuracy
- **Definition**: Percentage of individual words correctly transcribed
- **Range**: 0.0 (0%) to 1.0 (100%)
- **More forgiving than exact match accuracy**

### Translation Metrics

#### 1. BLEU Score (Translation)
- **Definition**: Standard metric for translation quality using n-gram precision
- **Range**: 0.0 (poor) to 1.0 (perfect)
- **Interpretation**:
  - ✅ **Excellent**: BLEU > 0.60
  - ✅ **Good**: BLEU > 0.40
  - ⚠️ **Fair**: BLEU > 0.20
  - ❌ **Poor**: BLEU ≤ 0.20

#### 2. F1 Score (Translation)
- **Definition**: Word-level overlap between reference and translated text
- **Range**: 0.0 (poor) to 1.0 (perfect)
- **Interpretation**:
  - ✅ **Excellent**: F1 > 0.85
  - ✅ **Good**: F1 > 0.70
  - ⚠️ **Fair**: F1 > 0.50
  - ❌ **Poor**: F1 ≤ 0.50

#### 3. Character Accuracy
- **Definition**: Percentage of characters correctly translated
- **Formula**: `1.0 - Character Error Rate`
- **Range**: 0.0 (0%) to 1.0 (100%)

#### 4. Semantic Similarity
- **Definition**: Jaccard similarity coefficient of word sets
- **Formula**: `|Intersection| / |Union|` of word sets
- **Range**: 0.0 (no similarity) to 1.0 (identical meaning)

#### 5. Length Ratio
- **Definition**: Ratio of translated text length to reference length
- **Optimal**: Close to 1.0
- **Helps identify over/under-translation**

## 🚀 Usage Guide

### Running Evaluation

#### Option 1: Direct Script Execution
```bash
cd multilingo-server
python evaluation.py
```

#### Option 2: API Endpoint
```bash
# Run new evaluation
curl -X POST "http://127.0.0.1:8001/api/admin/run-evaluation"

# Get latest metrics
curl -X GET "http://127.0.0.1:8001/api/admin/evaluation-metrics"
```

#### Option 3: Programmatic Usage
```python
from evaluation import VoxScribeEvaluator

# Initialize evaluator
evaluator = VoxScribeEvaluator()

# Evaluate speech-to-text
stt_metrics = evaluator.evaluate_speech_to_text(test_texts)

# Evaluate translation
translation_metrics = evaluator.evaluate_translation(
    source_texts, target_texts, "en", "fr"
)

# Generate report
report_path = evaluator.generate_evaluation_report()
```

### Test Data Format

#### Speech-to-Text Test Data
```python
test_texts = [
    "Hello, how are you today?",
    "The weather is nice outside.",
    # ... more test sentences
]
```

#### Translation Test Data
```python
english_texts = ["Hello, how are you?", ...]
french_translations = ["Bonjour, comment allez-vous?", ...]
```

## 📁 Output Files

### Generated Files
- `evaluation_results/stt_results_YYYYMMDD_HHMMSS.csv` - Detailed STT results
- `evaluation_results/stt_metrics_YYYYMMDD_HHMMSS.json` - STT metric summary
- `evaluation_results/translation_results_en_fr_YYYYMMDD_HHMMSS.csv` - Translation results
- `evaluation_results/translation_metrics_en_fr_YYYYMMDD_HHMMSS.json` - Translation metrics
- `evaluation_results/evaluation_report_YYYYMMDD_HHMMSS.md` - Comprehensive report
- `evaluation_results/evaluation.log` - Evaluation logs

### CSV File Structure

#### STT Results CSV
```csv
reference,prediction,correct,wer,f1
"Hello world","Hello world",True,0.0,1.0
"How are you","How are you",True,0.0,1.0
```

#### Translation Results CSV
```csv
source_text,reference_translation,predicted_translation,correct,bleu,f1
"Hello","Bonjour","Bonjour",True,1.0,1.0
"Thank you","Merci","Merci",True,1.0,1.0
```

## 🎯 Performance Benchmarks

### Industry Standard Benchmarks

#### Speech-to-Text Performance Levels
| Level | WER Range | CER Range | F1 Range | Use Case |
|-------|-----------|-----------|----------|----------|
| Production Ready | < 0.15 | < 0.10 | > 0.85 | Commercial deployment |
| Good | 0.15-0.25 | 0.10-0.20 | 0.70-0.85 | Beta testing |
| Fair | 0.25-0.35 | 0.20-0.30 | 0.50-0.70 | Development |
| Poor | > 0.35 | > 0.30 | < 0.50 | Needs improvement |

#### Translation Performance Levels
| Level | BLEU Range | F1 Range | Accuracy Range | Use Case |
|-------|------------|----------|----------------|----------|
| Excellent | > 0.60 | > 0.85 | > 0.80 | Professional quality |
| Good | 0.40-0.60 | 0.70-0.85 | 0.60-0.80 | Commercial deployment |
| Fair | 0.20-0.40 | 0.50-0.70 | 0.40-0.60 | Beta testing |
| Poor | < 0.20 | < 0.50 | < 0.40 | Needs improvement |

### VoxScribe Current Performance

**Latest Evaluation Results:**
- **Speech-to-Text**: WER: 0.1568 ✅, F1: 0.9116 ✅ → **Good Performance**
- **Translation**: BLEU: 0.4667 ✅, F1: 0.7961 ✅ → **Good Performance**
- **Overall Score**: 0.7544 → **Good Performance** ✅

## 📈 Monitoring and Alerts

### Automated Monitoring
```python
# Set up performance thresholds
PERFORMANCE_THRESHOLDS = {
    "stt": {
        "wer_max": 0.20,
        "f1_min": 0.80,
        "cer_max": 0.15
    },
    "translation": {
        "bleu_min": 0.35,
        "f1_min": 0.65,
        "accuracy_min": 0.40
    }
}

def check_performance_alerts(metrics):
    alerts = []
    
    # Check STT thresholds
    if metrics["stt"]["word_error_rate"] > PERFORMANCE_THRESHOLDS["stt"]["wer_max"]:
        alerts.append("STT: Word Error Rate too high")
    
    # Check translation thresholds
    if metrics["translation"]["bleu_score"] < PERFORMANCE_THRESHOLDS["translation"]["bleu_min"]:
        alerts.append("Translation: BLEU score too low")
    
    return alerts
```

## 🔧 Customization

### Adding New Metrics
```python
class CustomEvaluator(VoxScribeEvaluator):
    def custom_metric(self, reference: str, hypothesis: str) -> float:
        # Implement your custom metric
        return score
    
    def _calculate_stt_metrics(self, references, hypotheses):
        metrics = super()._calculate_stt_metrics(references, hypotheses)
        
        # Add custom metric
        custom_scores = [self.custom_metric(ref, hyp) 
                        for ref, hyp in zip(references, hypotheses)]
        metrics["custom_score"] = np.mean(custom_scores)
        
        return metrics
```

### Custom Test Data
```python
# Load your own test dataset
def load_custom_dataset():
    # Load from your data source
    return source_texts, target_texts

# Run evaluation with custom data
source_texts, target_texts = load_custom_dataset()
metrics = evaluator.evaluate_translation(source_texts, target_texts, "en", "fr")
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Install required dependencies
pip install pandas numpy
```

#### 2. No Evaluation Results
```python
# Check if evaluation has been run
from pathlib import Path
results_dir = Path("evaluation_results")
if not results_dir.exists():
    print("Run evaluation first: python evaluation.py")
```

#### 3. Low Performance Scores
- **Check test data quality**: Ensure ground truth is accurate
- **Verify model configuration**: Check Whisper model size and translation settings
- **Review error patterns**: Analyze CSV files for common failure modes

#### 4. File Permission Issues
```bash
# Ensure write permissions for evaluation_results directory
chmod 755 evaluation_results/
```

## 📚 API Reference

### GET /api/admin/evaluation-metrics
**Description**: Retrieve latest evaluation metrics
**Response**:
```json
{
  "evaluation_available": true,
  "last_evaluation": "20250627_003800",
  "speech_to_text": {
    "word_error_rate": 0.1568,
    "f1_score": 0.9116,
    "accuracy": 0.3333
  },
  "translation": {
    "bleu_score": 0.4667,
    "f1_score": 0.7961,
    "accuracy": 0.4667
  },
  "overall_score": 0.7544,
  "performance_assessment": "Good"
}
```

### POST /api/admin/run-evaluation
**Description**: Execute new evaluation and return results
**Response**:
```json
{
  "message": "Evaluation completed successfully",
  "speech_to_text": { /* STT metrics */ },
  "translation": { /* Translation metrics */ },
  "overall_score": 0.7544,
  "performance_assessment": "Good"
}
```

## 🎓 Best Practices

### 1. Regular Evaluation
- Run evaluations after model updates
- Schedule weekly performance checks
- Monitor trends over time

### 2. Test Data Management
- Use diverse, representative test sets
- Update test data periodically
- Maintain separate dev/test splits

### 3. Performance Monitoring
- Set up automated alerts
- Track metric trends
- Investigate performance drops immediately

### 4. Documentation
- Document evaluation procedures
- Record performance baselines
- Share results with stakeholders

## 📞 Support

For issues or questions about the evaluation framework:

1. **Check the logs**: `evaluation_results/evaluation.log`
2. **Review error patterns**: Analyze CSV output files
3. **Verify dependencies**: Ensure all required packages are installed
4. **Test with minimal data**: Start with small test sets

## 🔮 Future Enhancements

### Planned Features
- **Real-time evaluation**: Continuous monitoring during live sessions
- **A/B testing framework**: Compare different model configurations
- **Multi-language support**: Extend beyond English-French pairs
- **Performance dashboards**: Web-based visualization of metrics
- **Automated retraining triggers**: Based on performance thresholds

### Contributing
To contribute new metrics or improvements:
1. Fork the evaluation framework
2. Implement new metrics following existing patterns
3. Add comprehensive tests
4. Update documentation
5. Submit pull request with performance analysis

---

*This documentation covers the complete VoxScribe Model Evaluation Framework. For technical support or feature requests, please refer to the project repository.* 