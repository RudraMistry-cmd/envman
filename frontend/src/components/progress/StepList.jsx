import StepItem from './StepItem'

export default function StepList({ steps }) {
  return (
    <div className="space-y-0">
      {steps.map((step, i) => (
        <StepItem
          key={step.id}
          step={step}
          index={i}
          isLast={i === steps.length - 1}
        />
      ))}
    </div>
  )
}
