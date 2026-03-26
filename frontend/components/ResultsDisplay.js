import { ScoreCard, ProgressBar, Badge, Alert } from './UI';
import { useState } from 'react';

export default function ResultsDisplay({ data, onDownload, downloading = false }) {
  if (!data) return null;

  const {
    overall_score = 5,
    skill_score = 5,
    keyword_score = 5,
    experience_score = 5,
    ats_compatibility_score = 5,
    matching_skills = [],
    missing_keywords = [],
    missing_skills = [],
    strengths = [],
    weaknesses = [],
    improvement_suggestions = [],
    ats_issues = [],
  } = data;

  const getScoreMessage = (score) => {
    if (score === 10) return 'Perfect Match!';
    if (score >= 8) return 'Excellent Fit';
    if (score >= 6) return 'Good Match';
    if (score >= 4) return 'Fair Match';
    return 'Needs Improvement';
  };

  const getScoreColor = (score) => {
    if (score >= 8) return '#27ae60';
    if (score >= 6) return '#f39c12';
    return '#e74c3c';
  };

  return (
    <div className="results-section">
      {/* Overall Score - Enhanced */}
      <div style={{ marginBottom: '40px' }}>
        <div className="grid grid-2">
          <div className="card" style={{ textAlign: 'center', padding: '30px', background: `linear-gradient(135deg, ${getScoreColor(overall_score)}15, transparent)`, borderLeft: `4px solid ${getScoreColor(overall_score)}` }}>
            <p style={{ fontSize: '14px', color: '#7f8c8d', marginBottom: '16px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Overall Match Score
            </p>
            <p style={{ fontSize: '48px', fontWeight: '700', color: getScoreColor(overall_score), marginBottom: '8px' }}>
              {overall_score}/10
            </p>
            <p style={{ fontSize: '16px', fontWeight: '600', color: 'var(--primary-color)' }}>
              {getScoreMessage(overall_score)}
            </p>
          </div>
          <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '30px' }}>
            <h3 style={{ fontSize: '16px', color: '#7f8c8d', marginBottom: '16px', fontWeight: '600' }}>
              📊 Quick Summary
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                <span>Skills Match:</span>
                <span style={{ fontWeight: '700', color: getScoreColor(skill_score) }}>{skill_score}/10</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                <span>Keywords:</span>
                <span style={{ fontWeight: '700', color: getScoreColor(keyword_score) }}>{keyword_score}/10</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                <span>Experience:</span>
                <span style={{ fontWeight: '700', color: getScoreColor(experience_score) }}>{experience_score}/10</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                <span>ATS Score:</span>
                <span style={{ fontWeight: '700', color: getScoreColor(ats_compatibility_score) }}>{ats_compatibility_score}/10</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Score Breakdown */}
      <div className="card" style={{ marginBottom: '40px' }}>
        <h3 className="card-title">📈 Detailed Score Breakdown</h3>
        
        <div style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '14px' }}>
            <span style={{ fontWeight: '600' }}>Skills Match</span>
            <span style={{ fontWeight: '700', color: getScoreColor(skill_score) }}>{skill_score}/10</span>
          </div>
          <ProgressBar score={skill_score} />
        </div>

        <div style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '14px' }}>
            <span style={{ fontWeight: '600' }}>Keywords Match</span>
            <span style={{ fontWeight: '700', color: getScoreColor(keyword_score) }}>{keyword_score}/10</span>
          </div>
          <ProgressBar score={keyword_score} />
        </div>

        <div style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '14px' }}>
            <span style={{ fontWeight: '600' }}>Experience Relevance</span>
            <span style={{ fontWeight: '700', color: getScoreColor(experience_score) }}>{experience_score}/10</span>
          </div>
          <ProgressBar score={experience_score} />
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '14px' }}>
            <span style={{ fontWeight: '600' }}>ATS Compatibility</span>
            <span style={{ fontWeight: '700', color: getScoreColor(ats_compatibility_score) }}>{ats_compatibility_score}/10</span>
          </div>
          <ProgressBar score={ats_compatibility_score} />
        </div>
      </div>

      {/* Matching Skills */}
      {matching_skills && matching_skills.length > 0 && (
        <div className="card" style={{ marginBottom: '40px' }}>
          <h3 className="card-title">✅ Matching Skills ({matching_skills.length})</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {matching_skills.slice(0, 10).map((skill, idx) => (
              <Badge key={idx} text={skill} type="success" />
            ))}
          </div>
        </div>
      )}

      {/* Strengths */}
      {strengths && strengths.length > 0 && (
        <div className="card" style={{ marginBottom: '40px', borderLeft: `4px solid ${getScoreColor(overall_score)}` }}>
          <h3 className="card-title">💪 Your Strengths</h3>
          <ul style={{ listStyle: 'none' }}>
            {strengths.map((strength, idx) => (
              <li key={idx} style={{ padding: '12px 0', fontSize: '14px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                <span style={{ color: 'var(--success-color)', fontWeight: 'bold' }}>✓</span>
                <span>{strength}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Weaknesses */}
      {weaknesses && weaknesses.length > 0 && (
        <div className="card" style={{ marginBottom: '40px', borderLeft: `4px solid #f39c12` }}>
          <h3 className="card-title">⚠️ Areas for Improvement</h3>
          <ul style={{ listStyle: 'none' }}>
            {weaknesses.map((weakness, idx) => (
              <li key={idx} style={{ padding: '12px 0', fontSize: '14px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                <span style={{ color: 'var(--warning-color)', fontWeight: 'bold' }}>!</span>
                <span>{weakness}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Missing Keywords */}
      {missing_keywords && missing_keywords.length > 0 && (
        <div className="card" style={{ marginBottom: '40px' }}>
          <h3 className="card-title">🔑 Missing Keywords ({missing_keywords.length})</h3>
          <p style={{ fontSize: '13px', color: '#7f8c8d', marginBottom: '16px' }}>Add these keywords to improve your match</p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {missing_keywords.slice(0, 15).map((keyword, idx) => (
              <Badge key={idx} text={keyword} type="warning" />
            ))}
          </div>
        </div>
      )}

      {/* Missing Skills */}
      {missing_skills && missing_skills.length > 0 && (
        <div className="card" style={{ marginBottom: '40px' }}>
          <h3 className="card-title">📚 Missing Skills</h3>
          <p style={{ fontSize: '13px', color: '#7f8c8d', marginBottom: '16px' }}>Skills mentioned in the job description but not in your resume</p>
          <ul style={{ listStyle: 'none' }}>
            {missing_skills.slice(0, 8).map((skill, idx) => (
              <li key={idx} style={{ padding: '10px 0', fontSize: '14px', borderBottom: 'none', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ color: 'var(--danger-color)' }}>→</span>
                <span>{skill}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Improvement Suggestions */}
      {improvement_suggestions && improvement_suggestions.length > 0 && (
        <div className="card" style={{ marginBottom: '40px', background: 'linear-gradient(135deg, #3498db15, transparent)' }}>
          <h3 className="card-title">💡 Top Improvement Suggestions</h3>
          <ul style={{ listStyle: 'none' }}>
            {improvement_suggestions.slice(0, 5).map((suggestion, idx) => (
              <li key={idx} style={{ padding: '12px 0', fontSize: '14px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                <span style={{ color: 'var(--secondary-color)', fontWeight: 'bold', minWidth: '24px' }}>{idx + 1}.</span>
                <span>{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Download Button - Enhanced */}
      <div className="card" style={{ 
        textAlign: 'center', 
        padding: '40px', 
        background: overall_score < 5 
          ? 'linear-gradient(135deg, #f39c1215, transparent)' 
          : 'linear-gradient(135deg, var(--secondary-color)15, transparent)',
        borderTop: `4px solid ${overall_score < 5 ? '#f39c12' : 'var(--secondary-color)'}`
      }}>
        {overall_score < 5 && (
          <div style={{ 
            background: 'rgba(243, 156, 18, 0.1)',
            border: '1px solid #f39c12',
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '20px'
          }}>
            <p style={{ fontSize: '14px', color: '#f39c12', fontWeight: '600', marginBottom: '8px' }}>
              ⚠️ Low Match Score
            </p>
            <p style={{ fontSize: '12px', color: '#7f8c8d', lineHeight: '1.5' }}>
              Your resume has a low match score. The AI has generated an optimized version below that better aligns with the job description. Download and update your resume accordingly.
            </p>
          </div>
        )}
        
        <h3 style={{ fontSize: '24px', fontWeight: '700', color: 'var(--primary-color)', marginBottom: '16px' }}>
          {overall_score < 5 ? 'Download Optimized Resume' : 'Ready to Apply?'}
        </h3>
        <p style={{ fontSize: '14px', color: '#7f8c8d', marginBottom: '24px', maxWidth: '500px', margin: '0 auto 24px' }}>
          {overall_score < 5 
            ? 'This resume has been regenerated with better keywords, formatting, and ATS compatibility based on the job description.' 
            : 'Download your optimized resume that\'s tailored to this job description and ready for ATS systems.'}
        </p>
        <button
          onClick={onDownload}
          disabled={downloading}
          className={`btn ${downloading ? 'btn-disabled' : 'btn-success'} btn-lg`}
          style={{ 
            marginBottom: '16px',
            width: '100%',
            maxWidth: '300px',
            fontSize: '16px',
            padding: '16px 32px'
          }}
        >
          {downloading ? '⏳ Generating PDF...' : '📥 Download Optimized Resume (PDF)'}
        </button>
        <p style={{ fontSize: '12px', color: '#95a5a6' }}>
          {overall_score < 5 
            ? 'This AI-generated resume is optimized for ATS systems and job description matching'
            : 'Your resume includes all relevant keywords and is optimized for ATS compatibility'}
        </p>
      </div>
    </div>
  );
}
