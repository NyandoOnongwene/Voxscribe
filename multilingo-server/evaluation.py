"""
VoxScribe Model Evaluation Framework
Evaluates speech-to-text accuracy, translation quality, and system performance
"""

import os
import json
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from pathlib import Path
import soundfile as sf
from dataclasses import dataclass
import logging

# Import our models
from whisper_engine import whisper_engine
from translator import text_translator
from utils import convert_audio_to_wav

# Evaluation metrics
from jiwer import wer, cer, mer, wil, wip  # Word Error Rate, Character Error Rate, etc.
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from bert_score import score as bert_score
import editdistance

@dataclass
class EvaluationResult:
    """Container for evaluation results"""
    metric_name: str
    score: float
    details: Dict
    timestamp: str

class VoxScribeEvaluator:
    """Comprehensive evaluation framework for VoxScribe system"""
    
    def __init__(self, results_dir: str = "evaluation_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.results_dir / 'evaluation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize ROUGE scorer
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        
        # Results storage
        self.results = []
        
    def word_error_rate(self, reference: str, hypothesis: str) -> float:
        """Calculate Word Error Rate (WER)"""
        ref_words = reference.split()
        hyp_words = hypothesis.split()
        
        # Create matrix for dynamic programming
        d = np.zeros((len(ref_words) + 1, len(hyp_words) + 1))
        
        # Initialize first row and column
        for i in range(len(ref_words) + 1):
            d[i][0] = i
        for j in range(len(hyp_words) + 1):
            d[0][j] = j
        
        # Fill the matrix
        for i in range(1, len(ref_words) + 1):
            for j in range(1, len(hyp_words) + 1):
                if ref_words[i-1] == hyp_words[j-1]:
                    d[i][j] = d[i-1][j-1]
                else:
                    d[i][j] = min(
                        d[i-1][j] + 1,      # deletion
                        d[i][j-1] + 1,      # insertion
                        d[i-1][j-1] + 1     # substitution
                    )
        
        return d[len(ref_words)][len(hyp_words)] / len(ref_words) if ref_words else 0.0
    
    def character_error_rate(self, reference: str, hypothesis: str) -> float:
        """Calculate Character Error Rate (CER)"""
        ref_chars = list(reference)
        hyp_chars = list(hypothesis)
        
        d = np.zeros((len(ref_chars) + 1, len(hyp_chars) + 1))
        
        for i in range(len(ref_chars) + 1):
            d[i][0] = i
        for j in range(len(hyp_chars) + 1):
            d[0][j] = j
        
        for i in range(1, len(ref_chars) + 1):
            for j in range(1, len(hyp_chars) + 1):
                if ref_chars[i-1] == hyp_chars[j-1]:
                    d[i][j] = d[i-1][j-1]
                else:
                    d[i][j] = min(
                        d[i-1][j] + 1,
                        d[i][j-1] + 1,
                        d[i-1][j-1] + 1
                    )
        
        return d[len(ref_chars)][len(hyp_chars)] / len(ref_chars) if ref_chars else 0.0
    
    def bleu_score(self, reference: str, hypothesis: str, n: int = 4) -> float:
        """Calculate BLEU score"""
        ref_tokens = reference.split()
        hyp_tokens = hypothesis.split()
        
        if not hyp_tokens:
            return 0.0
        
        # Calculate n-gram precisions
        precisions = []
        for i in range(1, n + 1):
            ref_ngrams = self._get_ngrams(ref_tokens, i)
            hyp_ngrams = self._get_ngrams(hyp_tokens, i)
            
            if not hyp_ngrams:
                precisions.append(0.0)
                continue
            
            overlap = 0
            for ngram in hyp_ngrams:
                if ngram in ref_ngrams:
                    overlap += min(hyp_ngrams[ngram], ref_ngrams[ngram])
            
            precision = overlap / sum(hyp_ngrams.values())
            precisions.append(precision)
        
        # Brevity penalty
        ref_len = len(ref_tokens)
        hyp_len = len(hyp_tokens)
        bp = 1.0 if hyp_len > ref_len else np.exp(1 - ref_len / hyp_len)
        
        # Calculate BLEU
        if any(p == 0 for p in precisions):
            return 0.0
        
        bleu = bp * np.exp(np.mean([np.log(p) for p in precisions]))
        return bleu
    
    def _get_ngrams(self, tokens: List[str], n: int) -> Dict[tuple, int]:
        """Get n-grams from tokens"""
        ngrams = {}
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i:i+n])
            ngrams[ngram] = ngrams.get(ngram, 0) + 1
        return ngrams
    
    def f1_score(self, reference: str, hypothesis: str) -> float:
        """Calculate F1 score based on word overlap"""
        ref_words = set(reference.lower().split())
        hyp_words = set(hypothesis.lower().split())
        
        if not ref_words and not hyp_words:
            return 1.0
        if not ref_words or not hyp_words:
            return 0.0
        
        overlap = len(ref_words & hyp_words)
        precision = overlap / len(hyp_words)
        recall = overlap / len(ref_words)
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * (precision * recall) / (precision + recall)
    
    def evaluate_speech_to_text(self, 
                              test_audio_files: List[str], 
                              ground_truth_texts: List[str],
                              languages: List[str] = None) -> Dict[str, float]:
        """
        Evaluate Whisper speech-to-text performance
        
        Args:
            test_audio_files: List of paths to audio files
            ground_truth_texts: List of ground truth transcriptions
            languages: List of language codes for each audio file
            
        Returns:
            Dictionary of evaluation metrics
        """
        self.logger.info("Starting Speech-to-Text Evaluation...")
        
        predictions = []
        processing_times = []
        confidence_scores = []
        
        for i, (audio_file, ground_truth) in enumerate(zip(test_audio_files, ground_truth_texts)):
            try:
                # Load and convert audio
                start_time = time.time()
                audio_data, sample_rate = sf.read(audio_file)
                
                # Ensure audio is in the right format for Whisper
                if len(audio_data.shape) > 1:
                    audio_data = audio_data.mean(axis=1)  # Convert to mono
                
                # Transcribe
                language = languages[i] if languages else None
                result = whisper_engine.transcribe(audio_data, language=language)
                
                processing_time = time.time() - start_time
                
                predictions.append(result["text"].strip())
                processing_times.append(processing_time)
                confidence_scores.append(result.get("confidence", 0.0))
                
                self.logger.info(f"Processed {i+1}/{len(test_audio_files)}: {os.path.basename(audio_file)}")
                
            except Exception as e:
                self.logger.error(f"Error processing {audio_file}: {e}")
                predictions.append("")
                processing_times.append(0.0)
                confidence_scores.append(0.0)
        
        # Calculate metrics
        metrics = self._calculate_stt_metrics(ground_truth_texts, predictions)
        
        # Add performance metrics
        metrics.update({
            "avg_processing_time": np.mean(processing_times),
            "avg_confidence_score": np.mean(confidence_scores),
            "total_files": len(test_audio_files),
            "successful_transcriptions": sum(1 for p in predictions if p.strip())
        })
        
        # Save results
        self._save_stt_results(test_audio_files, ground_truth_texts, predictions, metrics)
        
        return metrics
    
    def evaluate_translation(self, 
                           source_texts: List[str],
                           target_texts: List[str],
                           source_lang: str,
                           target_lang: str) -> Dict[str, float]:
        """
        Evaluate translation quality
        
        Args:
            source_texts: List of source language texts
            target_texts: List of ground truth target language texts
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Dictionary of evaluation metrics
        """
        self.logger.info(f"Starting Translation Evaluation ({source_lang} -> {target_lang})...")
        
        predictions = []
        processing_times = []
        
        for i, source_text in enumerate(source_texts):
            try:
                start_time = time.time()
                translated = text_translator.translate(source_text, source_lang, target_lang)
                processing_time = time.time() - start_time
                
                predictions.append(translated)
                processing_times.append(processing_time)
                
                self.logger.info(f"Translated {i+1}/{len(source_texts)}")
                
            except Exception as e:
                self.logger.error(f"Error translating text {i}: {e}")
                predictions.append("")
                processing_times.append(0.0)
        
        # Calculate metrics
        metrics = self._calculate_translation_metrics(target_texts, predictions)
        
        # Add performance metrics
        metrics.update({
            "avg_processing_time": np.mean(processing_times),
            "total_translations": len(source_texts),
            "successful_translations": sum(1 for p in predictions if p.strip())
        })
        
        # Save results
        self._save_translation_results(source_texts, target_texts, predictions, metrics, source_lang, target_lang)
        
        return metrics
    
    def evaluate_end_to_end(self,
                          audio_files: List[str],
                          source_ground_truth: List[str],
                          target_ground_truth: List[str],
                          source_lang: str,
                          target_lang: str) -> Dict[str, float]:
        """
        Evaluate complete pipeline: Speech -> Text -> Translation
        
        Args:
            audio_files: List of audio file paths
            source_ground_truth: Ground truth transcriptions
            target_ground_truth: Ground truth translations
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Dictionary of evaluation metrics
        """
        self.logger.info("Starting End-to-End Evaluation...")
        
        transcriptions = []
        translations = []
        total_processing_times = []
        
        for i, audio_file in enumerate(audio_files):
            try:
                start_time = time.time()
                
                # Step 1: Transcribe
                audio_data, _ = sf.read(audio_file)
                if len(audio_data.shape) > 1:
                    audio_data = audio_data.mean(axis=1)
                
                transcription_result = whisper_engine.transcribe(audio_data, language=source_lang)
                transcription = transcription_result["text"].strip()
                
                # Step 2: Translate
                if transcription:
                    translation = text_translator.translate(transcription, source_lang, target_lang)
                else:
                    translation = ""
                
                total_time = time.time() - start_time
                
                transcriptions.append(transcription)
                translations.append(translation)
                total_processing_times.append(total_time)
                
                self.logger.info(f"Processed E2E {i+1}/{len(audio_files)}")
                
            except Exception as e:
                self.logger.error(f"Error in E2E processing {audio_file}: {e}")
                transcriptions.append("")
                translations.append("")
                total_processing_times.append(0.0)
        
        # Calculate metrics for both stages
        stt_metrics = self._calculate_stt_metrics(source_ground_truth, transcriptions)
        translation_metrics = self._calculate_translation_metrics(target_ground_truth, translations)
        
        # Combine metrics with prefixes
        e2e_metrics = {}
        for key, value in stt_metrics.items():
            e2e_metrics[f"stt_{key}"] = value
        for key, value in translation_metrics.items():
            e2e_metrics[f"translation_{key}"] = value
        
        e2e_metrics.update({
            "avg_total_processing_time": np.mean(total_processing_times),
            "total_files": len(audio_files)
        })
        
        # Save results
        self._save_e2e_results(audio_files, source_ground_truth, target_ground_truth, 
                              transcriptions, translations, e2e_metrics)
        
        return e2e_metrics
    
    def _calculate_stt_metrics(self, references: List[str], hypotheses: List[str]) -> Dict[str, float]:
        """Calculate speech-to-text evaluation metrics"""
        
        # Filter out empty predictions for fair evaluation
        filtered_pairs = [(ref, hyp) for ref, hyp in zip(references, hypotheses) if hyp.strip()]
        
        if not filtered_pairs:
            return {"error": "No valid predictions to evaluate"}
        
        filtered_refs, filtered_hyps = zip(*filtered_pairs)
        
        metrics = {}
        
        try:
            # Word Error Rate (lower is better)
            wer_scores = [self.word_error_rate(ref, hyp) for ref, hyp in zip(filtered_refs, filtered_hyps)]
            metrics["word_error_rate"] = np.mean(wer_scores)
            
            # Character Error Rate (lower is better)
            cer_scores = [self.character_error_rate(ref, hyp) for ref, hyp in zip(filtered_refs, filtered_hyps)]
            metrics["character_error_rate"] = np.mean(cer_scores)
            
            # Match Error Rate (lower is better)
            mer_scores = [mer(ref, hyp) for ref, hyp in zip(filtered_refs, filtered_hyps)]
            metrics["match_error_rate"] = np.mean(mer_scores)
            
            # Word Information Lost (lower is better)
            wil_scores = [wil(ref, hyp) for ref, hyp in zip(filtered_refs, filtered_hyps)]
            metrics["word_info_lost"] = np.mean(wil_scores)
            
            # Word Information Preserved (higher is better)
            wip_scores = [wip(ref, hyp) for ref, hyp in zip(filtered_refs, filtered_hyps)]
            metrics["word_info_preserved"] = np.mean(wip_scores)
            
            # Exact match accuracy
            exact_matches = sum(1 for ref, hyp in zip(filtered_refs, filtered_hyps) 
                              if ref.strip().lower() == hyp.strip().lower())
            metrics["exact_match_accuracy"] = exact_matches / len(filtered_pairs)
            
            # Length-normalized edit distance
            edit_distances = [editdistance.eval(ref, hyp) for ref, hyp in zip(filtered_refs, filtered_hyps)]
            avg_edit_distance = np.mean(edit_distances)
            avg_ref_length = np.mean([len(ref) for ref in filtered_refs])
            metrics["normalized_edit_distance"] = avg_edit_distance / max(avg_ref_length, 1)
            
        except Exception as e:
            self.logger.error(f"Error calculating STT metrics: {e}")
            metrics["error"] = str(e)
        
        return metrics
    
    def _calculate_translation_metrics(self, references: List[str], predictions: List[str]) -> Dict[str, float]:
        """Calculate translation evaluation metrics"""
        
        # Filter out empty predictions
        filtered_pairs = [(ref, pred) for ref, pred in zip(references, predictions) if pred.strip()]
        
        if not filtered_pairs:
            return {"error": "No valid predictions to evaluate"}
        
        filtered_refs, filtered_preds = zip(*filtered_pairs)
        
        metrics = {}
        
        try:
            # BLEU Score (0-1, higher is better)
            bleu_scores = [self.bleu_score(ref, pred) for ref, pred in zip(filtered_refs, filtered_preds)]
            metrics["bleu_score"] = np.mean(bleu_scores)
            
            # ROUGE Scores
            rouge_1_scores = []
            rouge_2_scores = []
            rouge_l_scores = []
            
            for ref, pred in zip(filtered_refs, filtered_preds):
                rouge_scores = self.rouge_scorer.score(ref, pred)
                rouge_1_scores.append(rouge_scores['rouge1'].fmeasure)
                rouge_2_scores.append(rouge_scores['rouge2'].fmeasure)
                rouge_l_scores.append(rouge_scores['rougeL'].fmeasure)
            
            metrics["rouge_1"] = np.mean(rouge_1_scores)
            metrics["rouge_2"] = np.mean(rouge_2_scores)
            metrics["rouge_l"] = np.mean(rouge_l_scores)
            
            # BERTScore (requires transformers, comment out if not available)
            try:
                P, R, F1 = bert_score(filtered_preds, filtered_refs, lang=None, verbose=False)
                metrics["bert_score_f1"] = F1.mean().item()
                metrics["bert_score_precision"] = P.mean().item()
                metrics["bert_score_recall"] = R.mean().item()
            except ImportError:
                self.logger.warning("BERTScore not available, skipping...")
            
            # Exact match accuracy
            exact_matches = sum(1 for ref, pred in zip(filtered_refs, filtered_preds) 
                              if ref.strip().lower() == pred.strip().lower())
            metrics["exact_match_accuracy"] = exact_matches / len(filtered_pairs)
            
            # Length-based metrics
            avg_ref_length = np.mean([len(ref.split()) for ref in filtered_refs])
            avg_pred_length = np.mean([len(pred.split()) for pred in filtered_preds])
            metrics["avg_reference_length"] = avg_ref_length
            metrics["avg_prediction_length"] = avg_pred_length
            metrics["length_ratio"] = avg_pred_length / max(avg_ref_length, 1)
            
        except Exception as e:
            self.logger.error(f"Error calculating translation metrics: {e}")
            metrics["error"] = str(e)
        
        return metrics
    
    def _save_stt_results(self, audio_files: List[str], references: List[str], 
                         predictions: List[str], metrics: Dict):
        """Save speech-to-text evaluation results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Detailed results
        results_df = pd.DataFrame({
            'audio_file': [os.path.basename(f) for f in audio_files],
            'reference': references,
            'prediction': predictions,
            'correct': [ref.strip().lower() == pred.strip().lower() 
                       for ref, pred in zip(references, predictions)]
        })
        
        results_df.to_csv(self.results_dir / f"stt_results_{timestamp}.csv", index=False)
        
        # Metrics summary
        with open(self.results_dir / f"stt_metrics_{timestamp}.json", 'w') as f:
            json.dump(metrics, f, indent=2)
        
        self.logger.info(f"STT results saved to {self.results_dir}")
    
    def _save_translation_results(self, sources: List[str], references: List[str], 
                                 predictions: List[str], metrics: Dict, 
                                 source_lang: str, target_lang: str):
        """Save translation evaluation results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Detailed results
        results_df = pd.DataFrame({
            'source_text': sources,
            'reference_translation': references,
            'predicted_translation': predictions,
            'correct': [ref.strip().lower() == pred.strip().lower() 
                       for ref, pred in zip(references, predictions)]
        })
        
        results_df.to_csv(self.results_dir / f"translation_results_{source_lang}_{target_lang}_{timestamp}.csv", 
                         index=False)
        
        # Metrics summary
        metrics['source_language'] = source_lang
        metrics['target_language'] = target_lang
        with open(self.results_dir / f"translation_metrics_{source_lang}_{target_lang}_{timestamp}.json", 'w') as f:
            json.dump(metrics, f, indent=2)
        
        self.logger.info(f"Translation results saved to {self.results_dir}")
    
    def _save_e2e_results(self, audio_files: List[str], source_refs: List[str], 
                         target_refs: List[str], transcriptions: List[str], 
                         translations: List[str], metrics: Dict):
        """Save end-to-end evaluation results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Detailed results
        results_df = pd.DataFrame({
            'audio_file': [os.path.basename(f) for f in audio_files],
            'source_reference': source_refs,
            'target_reference': target_refs,
            'transcription': transcriptions,
            'translation': translations,
            'stt_correct': [ref.strip().lower() == trans.strip().lower() 
                           for ref, trans in zip(source_refs, transcriptions)],
            'translation_correct': [ref.strip().lower() == trans.strip().lower() 
                                  for ref, trans in zip(target_refs, translations)]
        })
        
        results_df.to_csv(self.results_dir / f"e2e_results_{timestamp}.csv", index=False)
        
        # Metrics summary
        with open(self.results_dir / f"e2e_metrics_{timestamp}.json", 'w') as f:
            json.dump(metrics, f, indent=2)
        
        self.logger.info(f"End-to-end results saved to {self.results_dir}")
    
    def generate_evaluation_report(self):
        """Generate a comprehensive evaluation report"""
        report_path = self.results_dir / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_path, 'w') as f:
            f.write("# VoxScribe Model Evaluation Report\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Find latest result files
            metric_files = list(self.results_dir.glob("*_metrics_*.json"))
            
            if metric_files:
                f.write("## Evaluation Results\n\n")
                
                for metric_file in sorted(metric_files, reverse=True)[:5]:  # Latest 5 results
                    with open(metric_file) as mf:
                        metrics = json.load(mf)
                    
                    f.write(f"### {metric_file.stem}\n\n")
                    for key, value in metrics.items():
                        if isinstance(value, float):
                            f.write(f"- **{key}**: {value:.4f}\n")
                        else:
                            f.write(f"- **{key}**: {value}\n")
                    f.write("\n")
            
            f.write("## Metric Interpretations\n\n")
            f.write("### Speech-to-Text Metrics\n")
            f.write("- **Word Error Rate (WER)**: Lower is better (0 = perfect)\n")
            f.write("- **Character Error Rate (CER)**: Lower is better (0 = perfect)\n")
            f.write("- **Exact Match Accuracy**: Higher is better (1 = perfect)\n\n")
            
            f.write("### Translation Metrics\n")
            f.write("- **BLEU Score**: Higher is better (1 = perfect)\n")
            f.write("- **ROUGE-1/2/L**: Higher is better (1 = perfect)\n")
            f.write("- **BERTScore**: Higher is better (1 = perfect)\n\n")
        
        self.logger.info(f"Evaluation report generated: {report_path}")
        return report_path


def create_sample_evaluation():
    """Create sample evaluation with realistic test data"""
    evaluator = VoxScribeEvaluator()
    
    # Sample English texts for STT evaluation
    english_texts = [
        "Hello, how are you today?",
        "The weather is nice outside.",
        "I need to go to the store.",
        "What time is the meeting?",
        "Thank you for your help.",
        "Please call me tomorrow.",
        "The project is almost complete.",
        "Can you send me the report?",
        "I will be there at five o'clock.",
        "Have a great day!"
    ]
    
    # Corresponding French translations
    french_translations = [
        "Bonjour, comment allez-vous aujourd'hui?",
        "Il fait beau dehors.",
        "Je dois aller au magasin.",
        "À quelle heure est la réunion?",
        "Merci pour votre aide.",
        "Appelez-moi demain s'il vous plaît.",
        "Le projet est presque terminé.",
        "Pouvez-vous m'envoyer le rapport?",
        "Je serai là à cinq heures.",
        "Passez une excellente journée!"
    ]
    
    print("=== VoxScribe Model Evaluation ===\n")
    
    # 1. Evaluate Speech-to-Text
    print("1. Evaluating Speech-to-Text Performance...")
    stt_metrics = evaluator.evaluate_speech_to_text(english_texts)
    
    print("\n📊 Speech-to-Text Results:")
    for metric, value in stt_metrics.items():
        if isinstance(value, float):
            print(f"  • {metric}: {value:.4f}")
        else:
            print(f"  • {metric}: {value}")
    
    # 2. Evaluate Translation (English to French)
    print("\n2. Evaluating Translation Performance (EN → FR)...")
    translation_metrics = evaluator.evaluate_translation(
        source_texts=english_texts,
        target_texts=french_translations,
        source_lang="en",
        target_lang="fr"
    )
    
    print("\n📊 Translation Results:")
    for metric, value in translation_metrics.items():
        if isinstance(value, float):
            print(f"  • {metric}: {value:.4f}")
        else:
            print(f"  • {metric}: {value}")
    
    # 3. Generate comprehensive report
    print("\n3. Generating Evaluation Report...")
    report_path = evaluator.generate_evaluation_report()
    print(f"📄 Report saved: {report_path}")
    
    # 4. Summary
    print("\n=== EVALUATION SUMMARY ===")
    print(f"Speech-to-Text Accuracy: {stt_metrics.get('exact_match_accuracy', 0):.2%}")
    print(f"Translation BLEU Score: {translation_metrics.get('bleu_score', 0):.4f}")
    
    return stt_metrics, translation_metrics


if __name__ == "__main__":
    # Run comprehensive evaluation
    create_sample_evaluation() 