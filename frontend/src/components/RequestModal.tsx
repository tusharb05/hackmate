interface Props {
	teamName: string;
	message: string;
	setMessage: (val: string) => void;
	onClose: () => void;
	onSend: () => void;
}

const RequestModal = ({
	teamName,
	message,
	setMessage,
	onClose,
	onSend,
}: Props) => {
	return (
		<div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex justify-center items-center z-50 p-4">
			<div className="bg-white p-6 rounded-2xl shadow-xl w-full max-w-md border border-slate-200">
				<h2 className="text-xl font-bold mb-1 text-slate-800">
					Request to Join Team
				</h2>
				<p className="text-slate-600 mb-4 font-semibold">“{teamName}”</p>
				<textarea
					className="w-full border border-slate-300 bg-slate-50 rounded-lg p-3 h-28 mb-4 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
					value={message}
					onChange={(e) => setMessage(e.target.value)}
					placeholder="Write a brief message to the team leader..."
				/>
				<div className="flex justify-end gap-3">
					<button
						onClick={onClose}
						className="px-5 py-2.5 text-sm font-medium text-gray-900 bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-100">
						Cancel
					</button>
					<button
						onClick={onSend}
						className="px-5 py-2.5 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300">
						Send Request
					</button>
				</div>
			</div>
		</div>
	);
};

export default RequestModal;
