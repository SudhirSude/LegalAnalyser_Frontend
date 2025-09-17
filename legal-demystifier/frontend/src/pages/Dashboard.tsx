import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  FileText, 
  AlertTriangle, 
  Shield, 
  Clock, 
  DollarSign,
  ChevronDown,
  ChevronRight,
  Download,
  ExternalLink
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import RiskGauge from "@/components/dashboard/RiskGauge";

const Dashboard = () => {
  const [expandedFlags, setExpandedFlags] = useState<string[]>([]);

  // Mock data - would come from backend
  const documentSummary = {
    title: "Residential Lease Agreement",
    summary: "This is a standard 12-month residential lease agreement for a two-bedroom apartment located at 123 Oak Street. The lease establishes a monthly rent of $2,400, requires a security deposit of $2,400, and includes standard tenant responsibilities for maintenance and utilities. The agreement contains several important clauses regarding lease termination, pet policies, and property modifications.",
    keyPoints: [
      { type: "obligation", text: "Monthly rent due on 1st of each month", icon: DollarSign },
      { type: "deadline", text: "30-day notice required for lease termination", icon: Clock },
      { type: "penalty", text: "Late fees of $50 after 5-day grace period", icon: AlertTriangle }
    ]
  };

  const riskScore = 65;

  const redFlags = [
    {
      id: "unilateral-termination",
      severity: "high",
      title: "Unilateral Termination Rights",
      originalText: "The Landlord may terminate this lease at any time with thirty (30) days written notice for any reason or no reason whatsoever, regardless of tenant compliance with lease terms.",
      explanation: "This clause gives the landlord excessive power to end your tenancy without cause, providing little security of tenure.",
      whyRisky: [
        "No protection against arbitrary eviction",
        "Landlord doesn't need cause to terminate",
        "Creates housing insecurity for tenant"
      ],
      suggestedAction: "Negotiate for mutual termination rights or require 'just cause' for landlord termination",
      pageNumber: 3
    },
    {
      id: "excessive-fees",
      severity: "medium",
      title: "Excessive Administrative Fees",
      originalText: "Tenant agrees to pay a $200 administrative fee for any lease modifications, $150 for late rent processing, and $100 for any maintenance requests deemed non-essential by Landlord.",
      explanation: "These fees are unusually high and give the landlord discretionary power over what constitutes 'essential' maintenance.",
      whyRisky: [
        "Fees significantly above market standard",
        "Subjective criteria for maintenance fees",
        "Could discourage legitimate maintenance requests"
      ],
      suggestedAction: "Request fee schedule aligned with local standards and clear maintenance criteria",
      pageNumber: 7
    },
    {
      id: "broad-liability",
      severity: "medium",
      title: "Broad Tenant Liability Waiver",
      originalText: "Tenant waives all claims against Landlord for any injuries, damages, or losses occurring on the premises, including but not limited to those caused by Landlord's negligence.",
      explanation: "This waiver attempts to protect the landlord even from their own negligent actions, which may not be legally enforceable.",
      whyRisky: [
        "Attempts to waive landlord's basic legal responsibilities",
        "May not be legally enforceable",
        "Shifts inappropriate risk to tenant"
      ],
      suggestedAction: "Limit waiver to exclude landlord negligence and maintain basic safety obligations",
      pageNumber: 12
    }
  ];

  const toggleFlag = (flagId: string) => {
    setExpandedFlags(prev => 
      prev.includes(flagId) 
        ? prev.filter(id => id !== flagId)
        : [...prev, flagId]
    );
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'risk-high';
      case 'medium': return 'risk-medium';
      case 'low': return 'risk-low';
      default: return 'muted-foreground';
    }
  };

  const getSeverityBg = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-risk-high/20';
      case 'medium': return 'bg-risk-medium/20';
      case 'low': return 'bg-risk-low/20';
      default: return 'bg-muted/20';
    }
  };

  return (
    <div className="min-h-screen bg-background neural-bg p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <h1 className="text-4xl font-orbitron font-bold cyber-glow mb-2">
            DOCUMENT ANALYSIS COMPLETE
          </h1>
          <p className="text-lg font-rajdhani text-muted-foreground">
            Your legal document has been analyzed for risks and simplified for clarity
          </p>
        </motion.div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Document Summary */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="lg:col-span-2"
          >
            <Card className="bg-cyber-dark/50 border-neon-blue/30 holo-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 font-orbitron text-neon-blue">
                  <FileText className="w-6 h-6" />
                  DOCUMENT SUMMARY
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="text-xl font-rajdhani font-semibold mb-3">
                    {documentSummary.title}
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {documentSummary.summary}
                  </p>
                </div>

                {/* Key Points */}
                <div>
                  <h4 className="font-rajdhani font-semibold mb-3 text-neon-cyan">
                    KEY HIGHLIGHTS
                  </h4>
                  <div className="grid gap-3">
                    {documentSummary.keyPoints.map((point, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 + index * 0.1 }}
                        className="flex items-center gap-3 p-3 rounded-lg bg-cyber-navy/30"
                      >
                        <point.icon className="w-5 h-5 text-neon-cyan" />
                        <span className="font-rajdhani">{point.text}</span>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Risk Score Gauge */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-6"
          >
            <Card className="bg-cyber-dark/50 border-neon-blue/30 holo-border">
              <CardHeader>
                <CardTitle className="font-orbitron text-neon-blue text-center">
                  RISK ANALYSIS
                </CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col items-center">
                <RiskGauge score={riskScore} />
                <div className="text-center mt-6">
                  <div className="text-2xl font-orbitron font-bold text-risk-medium">
                    MEDIUM RISK
                  </div>
                  <div className="text-sm text-muted-foreground mt-2">
                    Score: {riskScore}/100
                  </div>
                  <p className="text-xs text-muted-foreground mt-3">
                    Based on {redFlags.length} identified risk factors
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Export Button */}
            <Button className="w-full bg-neon-magenta hover:bg-neon-purple text-cyber-void font-rajdhani font-semibold">
              <Download className="w-5 h-5 mr-2" />
              EXPORT REPORT
            </Button>
          </motion.div>
        </div>

        {/* Red Flags Section */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="bg-cyber-dark/50 border-neon-blue/30 holo-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-3 font-orbitron text-neon-blue">
                <AlertTriangle className="w-6 h-6" />
                IDENTIFIED RISKS & RED FLAGS
              </CardTitle>
            </CardHeader>
            <CardContent>
              {redFlags.length === 0 ? (
                <div className="text-center py-12">
                  <Shield className="w-16 h-16 text-neon-green mx-auto mb-4" />
                  <div className="text-xl font-rajdhani font-semibold text-neon-green">
                    No major risks detected!
                  </div>
                  <p className="text-muted-foreground mt-2">
                    This document appears to have standard, reasonable terms.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {redFlags.map((flag, index) => (
                    <motion.div
                      key={flag.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.4 + index * 0.1 }}
                      className="border border-muted rounded-lg overflow-hidden"
                    >
                      <button
                        onClick={() => toggleFlag(flag.id)}
                        className="w-full p-4 text-left hover:bg-cyber-navy/30 transition-colors flex items-center justify-between"
                      >
                        <div className="flex items-center gap-3">
                          <span className={`px-3 py-1 rounded-full text-xs font-rajdhani font-bold ${getSeverityBg(flag.severity)} text-${getSeverityColor(flag.severity)}`}>
                            {flag.severity.toUpperCase()}
                          </span>
                          <span className="font-rajdhani font-semibold">
                            {flag.title}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            Page {flag.pageNumber}
                          </span>
                        </div>
                        {expandedFlags.includes(flag.id) ? (
                          <ChevronDown className="w-5 h-5" />
                        ) : (
                          <ChevronRight className="w-5 h-5" />
                        )}
                      </button>

                      <AnimatePresence>
                        {expandedFlags.includes(flag.id) && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: "auto", opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.3 }}
                            className="overflow-hidden"
                          >
                            <div className="p-6 pt-0 space-y-6">
                              {/* Original Text */}
                              <div>
                                <h5 className="font-rajdhani font-semibold mb-2 text-neon-cyan">
                                  ORIGINAL TEXT
                                </h5>
                                <div className="p-4 bg-cyber-navy/30 rounded-lg border-l-4 border-neon-cyan">
                                  <p className="text-sm font-mono italic">
                                    "{flag.originalText}"
                                  </p>
                                </div>
                              </div>

                              {/* Explanation */}
                              <div>
                                <h5 className="font-rajdhani font-semibold mb-2 text-neon-cyan">
                                  SIMPLIFIED EXPLANATION
                                </h5>
                                <p className="text-muted-foreground">
                                  {flag.explanation}
                                </p>
                              </div>

                              {/* Why Risky */}
                              <div>
                                <h5 className="font-rajdhani font-semibold mb-2 text-neon-cyan">
                                  WHY THIS IS RISKY
                                </h5>
                                <ul className="space-y-1">
                                  {flag.whyRisky.map((risk, idx) => (
                                    <li key={idx} className="flex items-center gap-2 text-sm text-muted-foreground">
                                      <AlertTriangle className="w-4 h-4 text-risk-medium" />
                                      {risk}
                                    </li>
                                  ))}
                                </ul>
                              </div>

                              {/* Suggested Action */}
                              <div>
                                <h5 className="font-rajdhani font-semibold mb-2 text-neon-green">
                                  SUGGESTED ACTION
                                </h5>
                                <p className="text-sm text-muted-foreground">
                                  {flag.suggestedAction}
                                </p>
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </motion.div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Educational Resources */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="text-center"
        >
          <h3 className="font-orbitron font-semibold mb-4 text-neon-cyan">
            LEARN MORE ABOUT YOUR RIGHTS
          </h3>
          <div className="flex flex-wrap justify-center gap-4">
            {[
              "Understanding Lease Agreements",
              "Tenant Rights & Responsibilities", 
              "When to Consult a Lawyer"
            ].map((topic, index) => (
              <Button
                key={index}
                variant="outline"
                className="border-neon-cyan/30 text-neon-cyan hover:bg-neon-cyan/10"
              >
                {topic}
                <ExternalLink className="w-4 h-4 ml-2" />
              </Button>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;