/**
 * @typedef {Object} LabFinding
 * @property {string} name
 * @property {string} value
 * @property {number|null} numeric_value
 * @property {string|null} unit
 * @property {string|null} reference_range
 * @property {'normal'|'high'|'low'|'abnormal'|'unknown'} flag
 *
 * @typedef {Object} ReportFindings
 * @property {LabFinding[]} findings
 * @property {string[]} notes
 * @property {string} summary
 * @property {'parsed'|'failed'|'not_applicable'} extraction_status
 *
 * @typedef {Object} Analysis
 * @property {number} id
 * @property {string} session_id
 * @property {string} summary
 * @property {string[]} symptoms
 * @property {string[]} observations
 * @property {string[]} possible_concerns
 * @property {'LOW'|'MODERATE'|'HIGH'} risk_level
 * @property {string[]} red_flags
 * @property {string[]} recommended_next_steps
 * @property {string[]} questions_for_doctor
 * @property {string} limitations
 * @property {string} disclaimer
 * @property {string} source
 * @property {boolean} safety_override
 */
export {}
