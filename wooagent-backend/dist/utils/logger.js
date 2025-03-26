"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.customLogger = exports.notifyLogListeners = exports.addLogListener = void 0;
const winston_1 = __importDefault(require("winston"));
const uuid_1 = require("uuid");
// הגדרת הפורמט של הלוג
const logFormat = winston_1.default.format.printf(({ level, message, timestamp, ...meta }) => {
    return JSON.stringify({
        id: meta.id || (0, uuid_1.v4)(),
        timestamp,
        level,
        message,
        agent: meta.agent || 'System',
        details: meta.details || null,
    });
});
// יצירת מופע Logger
const logger = winston_1.default.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: winston_1.default.format.combine(winston_1.default.format.timestamp(), logFormat),
    transports: [
        new winston_1.default.transports.Console(),
        new winston_1.default.transports.File({ filename: 'logs/error.log', level: 'error' }),
        new winston_1.default.transports.File({ filename: 'logs/combined.log' })
    ],
});
// פונקציה לשליחת לוגים לכל המאזינים
let logListeners = [];
// הוספת מאזין ללוגים
const addLogListener = (listener) => {
    logListeners.push(listener);
    return () => {
        logListeners = logListeners.filter(l => l !== listener);
    };
};
exports.addLogListener = addLogListener;
// שליחת לוג לכל המאזינים
const notifyLogListeners = (logEntry) => {
    logListeners.forEach(listener => {
        try {
            listener(logEntry);
        }
        catch (error) {
            console.error('Error notifying log listener:', error);
        }
    });
};
exports.notifyLogListeners = notifyLogListeners;
// פונקציה מסייעת ליצירת מופע לוג
const createLogEntry = (level, message, meta = {}) => {
    return {
        id: meta.id || (0, uuid_1.v4)(),
        timestamp: new Date().toISOString(),
        level,
        message,
        agent: meta.agent || 'System',
        details: meta.details || null,
    };
};
// פונקציה מותאמת אישית לתיעוד ושליחת התראות
exports.customLogger = {
    info: (message, meta = {}) => {
        const entry = createLogEntry('info', message, meta);
        (0, exports.notifyLogListeners)(entry);
        logger.info(message, { ...meta });
    },
    error: (message, meta = {}) => {
        const entry = createLogEntry('error', message, meta);
        (0, exports.notifyLogListeners)(entry);
        logger.error(message, { ...meta });
    },
    warn: (message, meta = {}) => {
        const entry = createLogEntry('warn', message, meta);
        (0, exports.notifyLogListeners)(entry);
        logger.warn(message, { ...meta });
    },
    debug: (message, meta = {}) => {
        const entry = createLogEntry('debug', message, meta);
        (0, exports.notifyLogListeners)(entry);
        logger.debug(message, { ...meta });
    }
};
// ייצוא הלוגר
exports.default = exports.customLogger;
//# sourceMappingURL=logger.js.map