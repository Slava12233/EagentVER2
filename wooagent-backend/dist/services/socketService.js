"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.socketService = void 0;
const socket_io_1 = require("socket.io");
const logger_1 = __importStar(require("../utils/logger"));
const logService_1 = require("./logService");
class SocketService {
    constructor() {
        this.io = null;
        this.activeSockets = new Set();
    }
    initialize(server) {
        this.io = new socket_io_1.Server(server, {
            cors: {
                origin: process.env.CLIENT_URL || "http://localhost:3000",
                methods: ["GET", "POST"],
                credentials: true
            }
        });
        this.io.on('connection', async (socket) => {
            const socketId = socket.id;
            this.activeSockets.add(socketId);
            logger_1.default.info(`Socket connected: ${socketId}`, { agent: 'SocketService' });
            // כאשר לקוח מתחבר, שלח אליו את כל הלוגים הקיימים
            socket.emit('connection_status', { isConnected: true });
            // שליחת היסטוריית לוגים אחרונים
            try {
                const recentLogs = await logService_1.logService.getLogs({ limit: 100 });
                if (recentLogs && recentLogs.length > 0) {
                    logger_1.default.info(`שולח ${recentLogs.length} לוגים אחרונים ללקוח חדש`, { agent: 'SocketService' });
                    socket.emit('log_history', recentLogs);
                }
            }
            catch (error) {
                logger_1.default.error(`שגיאה בשליחת היסטוריית לוגים: ${error}`, { agent: 'SocketService' });
            }
            // מאזין לבקשות התנתקות
            socket.on('disconnect', () => {
                this.activeSockets.delete(socketId);
                logger_1.default.info(`Socket disconnected: ${socketId}`, { agent: 'SocketService' });
            });
            // מאזין לבקשות לוגים
            socket.on('get_logs', async (data) => {
                try {
                    const recentLogs = await logService_1.logService.getLogs({
                        limit: data.limit || 100
                    });
                    socket.emit('log_history', recentLogs);
                }
                catch (error) {
                    logger_1.default.error(`שגיאה בשליחת היסטוריית לוגים: ${error}`, { agent: 'SocketService' });
                }
            });
            // מאזין לבקשות צ'אט
            socket.on('chat_message', (data) => {
                // כאן נעביר את ההודעה למודול הטיפול בצ'אט
                logger_1.default.info(`Received chat message: ${JSON.stringify(data)}`, { agent: 'SocketService' });
            });
        });
        // התחברות למערכת הלוגים להעברת עדכונים בזמן אמת
        (0, logger_1.addLogListener)((logEntry) => {
            if (this.io) {
                this.io.emit('log', logEntry);
            }
        });
        logger_1.default.info('Socket.IO service initialized', { agent: 'SocketService' });
    }
    sendLogUpdate(logEntry) {
        if (!this.io) {
            logger_1.default.warn('Attempted to send log update before Socket.IO initialization', { agent: 'SocketService' });
            return;
        }
        this.io.emit('log', logEntry);
    }
    sendChatResponse(userId, response) {
        if (!this.io) {
            logger_1.default.warn('Attempted to send chat response before Socket.IO initialization', { agent: 'SocketService' });
            return;
        }
        this.io.emit('chat_response', { userId, ...response });
    }
    broadcastAgentStatus(status) {
        if (!this.io) {
            logger_1.default.warn('Attempted to broadcast agent status before Socket.IO initialization', { agent: 'SocketService' });
            return;
        }
        this.io.emit('agent_status', status);
    }
    getActiveConnections() {
        return this.activeSockets.size;
    }
}
// יצירת מופע יחיד של השירות
exports.socketService = new SocketService();
exports.default = exports.socketService;
//# sourceMappingURL=socketService.js.map