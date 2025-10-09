import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Message } from "../hooks/useChat";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "../../../components/ui/collapsible";
import { ChevronDown } from "lucide-react";
import { FeedbackControls } from "./FeedbackControls";

interface MessageListProps {
  messages: Message[];
  isStreaming: boolean;
  onFeedbackChange?: (
    historyId: number,
    score: number,
    comment: string | null,
  ) => void;
}

interface MarkdownContentProps {
  content: string;
}

const MarkdownContent = ({ content }: MarkdownContentProps) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ children }) => (
          <h1 className="text-2xl font-bold text-secondary-900 mt-6 mb-4 pb-2 border-b-2 border-primary-200">
            {children}
          </h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-xl font-bold text-secondary-900 mt-5 mb-3">
            {children}
          </h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-lg font-semibold text-secondary-800 mt-4 mb-2">
            {children}
          </h3>
        ),
        h4: ({ children }) => (
          <h4 className="text-base font-semibold text-secondary-800 mt-3 mb-2">
            {children}
          </h4>
        ),
        p: ({ children }) => (
          <p className="text-secondary-700 leading-relaxed my-3">{children}</p>
        ),
        ul: ({ children }) => (
          <ul className="list-disc list-inside space-y-2 my-3 ml-4 text-secondary-700">
            {children}
          </ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal list-inside space-y-2 my-3 ml-4 text-secondary-700">
            {children}
          </ol>
        ),
        li: ({ children }) => <li className="leading-relaxed">{children}</li>,
        code: ({ className, children, ...props }) => {
          const isInline = !className;
          if (isInline) {
            return (
              <code className="bg-secondary-100 text-primary-700 px-1.5 py-0.5 rounded text-sm font-mono">
                {children}
              </code>
            );
          }
          return (
            <code className={className} {...props}>
              {children}
            </code>
          );
        },
        pre: ({ children }) => (
          <pre className="bg-secondary-900 text-secondary-100 p-4 rounded-lg overflow-x-auto my-4 font-mono text-sm">
            {children}
          </pre>
        ),
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-primary-500 pl-4 py-2 my-4 italic text-secondary-600 bg-primary-50 rounded-r">
            {children}
          </blockquote>
        ),
        a: ({ href, children }) => (
          <a
            href={href}
            className="text-primary-600 hover:text-primary-700 underline font-medium"
            target="_blank"
            rel="noopener noreferrer"
          >
            {children}
          </a>
        ),
        table: ({ children }) => (
          <div className="overflow-x-auto my-4">
            <table className="min-w-full divide-y divide-secondary-200 border border-secondary-200 rounded-lg">
              {children}
            </table>
          </div>
        ),
        thead: ({ children }) => (
          <thead className="bg-secondary-100">{children}</thead>
        ),
        tbody: ({ children }) => (
          <tbody className="bg-white divide-y divide-secondary-200">
            {children}
          </tbody>
        ),
        tr: ({ children }) => (
          <tr className="hover:bg-secondary-50">{children}</tr>
        ),
        th: ({ children }) => (
          <th className="px-4 py-3 text-left text-xs font-semibold text-secondary-700 uppercase tracking-wider">
            {children}
          </th>
        ),
        td: ({ children }) => (
          <td className="px-4 py-3 text-sm text-secondary-600">{children}</td>
        ),
        strong: ({ children }) => (
          <strong className="font-bold text-secondary-900">{children}</strong>
        ),
        em: ({ children }) => (
          <em className="italic text-secondary-700">{children}</em>
        ),
        hr: () => <hr className="my-6 border-t-2 border-secondary-200" />,
      }}
    >
      {content}
    </ReactMarkdown>
  );
};

export const MessageList = ({
  messages,
  isStreaming,
  onFeedbackChange,
}: MessageListProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [expandedCitations, setExpandedCitations] = useState<Set<string>>(
    new Set(),
  );

  const toggleCitation = (messageId: string, citationIdx: number) => {
    const key = `${messageId}-${citationIdx}`;
    setExpandedCitations((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(key)) {
        newSet.delete(key);
      } else {
        newSet.add(key);
      }
      return newSet;
    });
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gradient-to-b from-secondary-50 to-white">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${
            message.role === "user" ? "justify-end" : "justify-start"
          }`}
        >
          <div
            className={`max-w-[75%] rounded-2xl p-5 shadow-md ${
              message.role === "user"
                ? "bg-gradient-to-br from-primary-600 to-primary-700 text-white"
                : "bg-white border-2 border-secondary-100"
            }`}
          >
            <div className="prose prose-sm max-w-none">
              {message.role === "user" ? (
                <div className="text-white whitespace-pre-wrap break-words">
                  {message.content}
                </div>
              ) : (
                <MarkdownContent content={message.content} />
              )}
            </div>

            {message.role === "assistant" &&
              message.citations &&
              message.citations.length > 0 && (
                <Collapsible className="mt-4 pt-4 border-t border-secondary-200">
                  <CollapsibleTrigger className="flex items-center gap-2 text-sm text-secondary-600 hover:text-primary-600 font-medium transition-colors">
                    <ChevronDown className="h-4 w-4" />
                    참고 자료 ({message.citations.length})
                  </CollapsibleTrigger>
                  <CollapsibleContent className="mt-3 space-y-2">
                    {message.citations.map((citation, idx) => {
                      const citationKey = `${message.id}-${idx}`;
                      const isExpanded = expandedCitations.has(citationKey);

                      return (
                        <div
                          key={citationKey}
                          role="button"
                          tabIndex={0}
                          className="text-sm bg-gradient-to-br from-secondary-50 to-white p-3 rounded-lg border border-secondary-200 hover:border-primary-300 transition-colors cursor-pointer"
                          onClick={() => toggleCitation(message.id, idx)}
                          onKeyDown={(e) => {
                            if (e.key === "Enter" || e.key === " ") {
                              e.preventDefault();
                              toggleCitation(message.id, idx);
                            }
                          }}
                        >
                          <div className="font-semibold text-secondary-800 flex items-center justify-between">
                            <span>{citation.title}</span>
                            <ChevronDown
                              className={`h-4 w-4 text-secondary-400 transition-transform ${
                                isExpanded ? "rotate-180" : ""
                              }`}
                            />
                          </div>
                          <div
                            className={`text-secondary-600 text-xs mt-1.5 ${
                              isExpanded ? "" : "line-clamp-2"
                            }`}
                          >
                            {citation.content}
                          </div>
                          {isExpanded && (
                            <div className="text-primary-600 text-xs mt-1 font-medium">
                              클릭하여 접기
                            </div>
                          )}
                          <div className="flex items-center gap-2 mt-2">
                            <div className="flex-1 bg-secondary-200 rounded-full h-1.5">
                              <div
                                className="bg-primary-500 h-1.5 rounded-full transition-all"
                                style={{ width: `${citation.score * 100}%` }}
                              />
                            </div>
                            <span className="text-secondary-500 text-xs font-medium">
                              {(citation.score * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </CollapsibleContent>
                </Collapsible>
              )}

            {message.role === "assistant" && message.historyId && (
              <div className="mt-4 border-t border-secondary-200 pt-4">
                <FeedbackControls
                  historyId={message.historyId}
                  initialScore={message.feedbackScore ?? 0}
                  initialComment={message.feedbackComment ?? ""}
                  disabled={isStreaming}
                  onChange={(score, comment) => {
                    if (message.historyId !== undefined) {
                      onFeedbackChange?.(message.historyId, score, comment);
                    }
                  }}
                />
              </div>
            )}
          </div>
        </div>
      ))}

      {isStreaming && (
        <div className="flex justify-start">
          <div className="bg-white border-2 border-primary-200 rounded-2xl p-5 shadow-md">
            <div className="flex items-center gap-3">
              <div className="flex gap-1">
                <div className="w-2.5 h-2.5 bg-primary-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-2.5 h-2.5 bg-primary-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-2.5 h-2.5 bg-primary-500 rounded-full animate-bounce"></div>
              </div>
              <span className="text-sm text-primary-700 font-medium">
                답변 생성 중...
              </span>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};
