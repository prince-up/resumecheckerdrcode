import React, { useState } from 'react';
import axios from 'axios';
import styles from '@/styles/components/QuestionForm.module.css';

const QuestionForm = ({ resumeText, jobDescription, isDisabled = false }) => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState('');

  const handleAsk = async (e) => {
    e.preventDefault();
    setError('');
    setResponse(null);

    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    if (!resumeText || !jobDescription) {
      setError('Please complete the analysis first');
      return;
    }

    setLoading(true);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const result = await axios.post(`${API_URL}/api/ask/question`, {
        resume_text: resumeText,
        job_description: jobDescription,
        question: question.trim(),
      });

      setResponse(result.data);
      setQuestion('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get answer. Please try again.');
      console.error('Question error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.questionFormWrapper}>
        <h3 className={styles.title}>
          💬 Ask a Question
        </h3>
        <p className={styles.subtitle}>
          Ask anything about your resume and how it matches the job
        </p>

        <form onSubmit={handleAsk} className={styles.form}>
          <div className={styles.inputGroup}>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g., Should I highlight more technical skills? How well does my experience match? What keywords should I add?"
              className={styles.textarea}
              disabled={loading || isDisabled}
              rows="3"
            />
          </div>

          <button
            type="submit"
            disabled={loading || isDisabled || !resumeText || !jobDescription}
            className={styles.button}
          >
            {loading ? (
              <>
                <span className={styles.spinner}></span>
                Analyzing...
              </>
            ) : (
              <>✨ Get AI Answer</>
            )}
          </button>

          {error && <div className={styles.error}>{error}</div>}
        </form>

        {response && (
          <div className={styles.responseWrapper}>
            <div className={styles.answerBox}>
              <h4 className={styles.answerTitle}>💡 AI Answer</h4>
              <p className={styles.answerText}>{response.answer}</p>

              {response.key_points && response.key_points.length > 0 && (
                <div className={styles.keyPoints}>
                  <h5 className={styles.keyPointsTitle}>Key Points:</h5>
                  <ul className={styles.keyPointsList}>
                    {response.key_points.map((point, idx) => (
                      <li key={idx} className={styles.keyPoint}>
                        {point}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {response.action_items && response.action_items.length > 0 && (
                <div className={styles.actionItems}>
                  <h5 className={styles.actionItemsTitle}>What You Can Do:</h5>
                  <ul className={styles.actionItemsList}>
                    {response.action_items.map((item, idx) => (
                      <li key={idx} className={styles.actionItem}>
                        ✓ {item}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <div className={styles.examplesWrapper}>
        <h4 className={styles.examplesTitle}>Example Questions:</h4>
        <div className={styles.examplesList}>
          <button
            type="button"
            className={styles.exampleButton}
            onClick={() => setQuestion('Should I add more technical skills to my resume?')}
            disabled={loading}
          >
            Should I add more technical skills?
          </button>
          <button
            type="button"
            className={styles.exampleButton}
            onClick={() => setQuestion('How well does my experience match this job description?')}
            disabled={loading}
          >
            How well does my experience match?
          </button>
          <button
            type="button"
            className={styles.exampleButton}
            onClick={() => setQuestion('What are the most important keywords I should highlight?')}
            disabled={loading}
          >
            What keywords should I highlight?
          </button>
          <button
            type="button"
            className={styles.exampleButton}
            onClick={() => setQuestion('How can I improve my summary section?')}
            disabled={loading}
          >
            How can I improve my summary?
          </button>
        </div>
      </div>
    </div>
  );
};

export default QuestionForm;
